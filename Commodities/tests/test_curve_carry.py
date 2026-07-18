from commodities.curve_carry import _annualized_slope, _classify


class TestAnnualizedSlope:
    def test_a_pricier_deferred_contract_gives_a_positive_slope(self):
        slope = _annualized_slope(a_close=100.0, b_close=102.0, month_gap=2)

        assert slope > 0

    def test_a_cheaper_deferred_contract_gives_a_negative_slope(self):
        slope = _annualized_slope(a_close=100.0, b_close=98.0, month_gap=2)

        assert slope < 0

    def test_zero_month_gap_is_undefined(self):
        slope = _annualized_slope(a_close=100.0, b_close=102.0, month_gap=0)

        assert slope != slope  # NaN

    def test_doubling_the_month_gap_halves_the_annualized_slope(self):
        one_month = _annualized_slope(a_close=100.0, b_close=102.0, month_gap=1)
        two_month = _annualized_slope(a_close=100.0, b_close=102.0, month_gap=2)

        assert two_month == one_month / 2


class TestClassify:
    def test_positive_slope_above_the_flat_band_is_contango(self):
        assert _classify(0.05) == "contango"

    def test_negative_slope_below_the_flat_band_is_backwardation(self):
        assert _classify(-0.05) == "backwardation"

    def test_slope_inside_the_flat_band_is_flat(self):
        assert _classify(0.005) == "flat"
        assert _classify(-0.005) == "flat"
