import pytest
from pet_boarding import boarding_fee, admission_ok, checkout_status


# ============================================================================
# Tests for boarding_fee(pet_type, days, is_premium)
# ============================================================================

def test_boarding_fee_unknown_pet():
    """Test unknown pet type raises ValueError."""
    with pytest.raises(ValueError, match="unknown pet type"):
        boarding_fee("parrot", 5, False)


def test_boarding_fee_invalid_days():
    """Test negative days raises ValueError."""
    with pytest.raises(ValueError, match="invalid days"):
        boarding_fee("dog", -1, False)


def test_boarding_fee_within_included_days():
    """Test stay within included days returns fee of 0."""
    # dog included is 2, days = 2 -> extra = 0 <= 0
    assert boarding_fee("dog", 2, False) == 0


def test_boarding_fee_dog_premium_short_stay():
    """Test dog with premium kennel and extra days <= 10."""
    # included = 2 + 1 = 3, extra = 5 - 3 = 2 <= 10, dog rate = 30
    assert boarding_fee("dog", 5, True) == 60


def test_boarding_fee_cat_standard_short_stay():
    """Test cat standard kennel and extra days <= 10."""
    # included = 3, extra = 5 - 3 = 2 <= 10, non-dog rate = 20
    assert boarding_fee("cat", 5, False) == 40


def test_boarding_fee_dog_long_stay():
    """Test dog long stay where extra > 10 (rate = 30 + 10 + 5 = 45)."""
    # included = 2, extra = 14 - 2 = 12 > 10
    assert boarding_fee("dog", 14, False) == 12 * 45


def test_boarding_fee_rabbit_premium_long_stay():
    """Test rabbit premium (rabbit does not get extra included day) and extra > 10."""
    # included = 4, extra = 16 - 4 = 12 > 10, non-dog rate = 20 + 10 = 30
    assert boarding_fee("rabbit", 16, True) == 12 * 30


# ============================================================================
# Tests for admission_ok(pet_age_years, vaccinations, is_senior)
# ============================================================================

def test_admission_ok_senior():
    """Test senior pet admission requires at least 3 vaccinations."""
    assert admission_ok(10, 3, True) is True
    assert admission_ok(10, 2, True) is False


def test_admission_ok_underage():
    """Test non-senior pet under 1 year is rejected."""
    assert admission_ok(0.5, 4, False) is False


def test_admission_ok_adult():
    """Test non-senior pet 1 year or older requires at least 2 vaccinations."""
    assert admission_ok(2, 2, False) is True
    assert admission_ok(2, 1, False) is False


# ============================================================================
# Tests for checkout_status(minutes_left, is_long_stay, is_weekend)
# ============================================================================

def test_checkout_status_long_stay_weekend():
    """Test long stay on weekend (cutoff = 30 + 20 = 50)."""
    assert checkout_status(55, True, True) == "open"
    assert checkout_status(40, True, True) == "late"
    assert checkout_status(30, True, True) == "closed"


def test_checkout_status_short_stay_weekday():
    """Test short stay on weekday (cutoff = 15)."""
    assert checkout_status(20, False, False) == "open"
    assert checkout_status(5, False, False) == "late"
    assert checkout_status(-5, False, False) == "closed"
