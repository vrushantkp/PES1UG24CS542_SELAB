import pytest
from pet_boarding import boarding_fee, admission_ok, checkout_status


# ============================================================================
# Branch Coverage Tests for boarding_fee(pet_type, days, is_premium)
# ============================================================================

def test_boarding_fee_branch_unknown_pet():
    """Branch: pet_type not in INCLUDED_DAYS -> True."""
    with pytest.raises(ValueError, match="unknown pet type"):
        boarding_fee("hamster", 3, False)


def test_boarding_fee_branch_negative_days():
    """Branch: days < 0 -> True."""
    with pytest.raises(ValueError, match="invalid days"):
        boarding_fee("dog", -1, False)


def test_boarding_fee_branch_extra_non_positive():
    """Branch: extra <= 0 -> True (both zero and negative extra)."""
    # dog included is 2, days = 2 -> extra = 0
    assert boarding_fee("dog", 2, False) == 0
    # dog included is 2, days = 1 -> extra = -1 <= 0
    assert boarding_fee("dog", 1, False) == 0


def test_boarding_fee_branch_premium_rabbit_compound():
    """
    Branch & Condition: is_premium and pet_type != 'rabbit'
    - Case A (True and False): is_premium=True, pet_type='rabbit' -> condition fails.
    - included stays 4, extra = 14 - 4 = 10 (extra <= 10), non-dog rate = 20.
    """
    assert boarding_fee("rabbit", 14, True) == 10 * 20


def test_boarding_fee_branch_dog_premium_short():
    """
    Branch & Condition: is_premium and pet_type != 'rabbit' -> evaluates to True.
    - dog included = 2 + 1 = 3.
    - extra = 6 - 3 = 3 <= 10 (extra > 10 False).
    - pet_type == 'dog' -> True (rate = 30).
    """
    assert boarding_fee("dog", 6, True) == 3 * 30


def test_boarding_fee_branch_non_dog_standard_short():
    """
    Branch: pet_type != 'dog' (rate = 20), extra <= 10.
    - cat included = 3, days = 8 -> extra = 5 <= 10.
    """
    assert boarding_fee("cat", 8, False) == 5 * 20


def test_boarding_fee_branch_dog_extra_over_10():
    """
    Branch: extra > 10 -> True AND pet_type == 'dog' -> True.
    - dog included = 2, days = 13 -> extra = 11 > 10.
    - rate = 30 + 10 + 5 = 45.
    """
    assert boarding_fee("dog", 13, False) == 11 * 45


def test_boarding_fee_branch_non_dog_extra_over_10():
    """
    Branch: extra > 10 -> True AND pet_type != 'dog' -> False (no dog surcharge).
    - cat included = 3, days = 14 -> extra = 11 > 10.
    - rate = 20 + 10 = 30.
    """
    assert boarding_fee("cat", 14, False) == 11 * 30


# ============================================================================
# Branch Coverage Tests for admission_ok(pet_age_years, vaccinations, is_senior)
# ============================================================================

def test_admission_ok_branch_senior_true():
    """Branch: is_senior -> True, vaccinations >= 3 -> True."""
    assert admission_ok(8, 3, True) is True


def test_admission_ok_branch_senior_false():
    """Branch: is_senior -> True, vaccinations >= 3 -> False."""
    assert admission_ok(8, 2, True) is False


def test_admission_ok_branch_underage():
    """Branch: is_senior -> False, pet_age_years < 1 -> True."""
    assert admission_ok(0.8, 5, False) is False


def test_admission_ok_branch_adult_vaccinated():
    """Branch: is_senior -> False, pet_age_years < 1 -> False, vaccinations >= 2 -> True."""
    assert admission_ok(1.0, 2, False) is True


def test_admission_ok_branch_adult_unvaccinated():
    """Branch: is_senior -> False, pet_age_years < 1 -> False, vaccinations >= 2 -> False."""
    assert admission_ok(1.0, 1, False) is False


# ============================================================================
# Branch Coverage Tests for checkout_status(minutes_left, is_long_stay, is_weekend)
# ============================================================================

@pytest.mark.parametrize(
    "minutes_left,is_long_stay,is_weekend,expected",
    [
        # Long stay + Weekend: cutoff = 30 + 20 = 50
        (50, True, True, "open"),     # minutes_left >= cutoff
        (49, True, True, "late"),     # minutes_left < cutoff and >= cutoff - 15 (35)
        (35, True, True, "late"),     # boundary: minutes_left == cutoff - 15
        (34, True, True, "closed"),   # minutes_left < cutoff - 15

        # Long stay + Weekday: cutoff = 30
        (30, True, False, "open"),
        (25, True, False, "late"),
        (14, True, False, "closed"),

        # Short stay + Weekend: cutoff = 15 + 20 = 35
        (35, False, True, "open"),
        (20, False, True, "late"),
        (19, False, True, "closed"),

        # Short stay + Weekday: cutoff = 15
        (15, False, False, "open"),
        (0, False, False, "late"),    # boundary: 15 - 15 = 0
        (-1, False, False, "closed"),
    ],
)
def test_checkout_status_all_decision_branches(minutes_left, is_long_stay, is_weekend, expected):
    """Test every branch combination for cutoff logic and return status."""
    assert checkout_status(minutes_left, is_long_stay, is_weekend) == expected
