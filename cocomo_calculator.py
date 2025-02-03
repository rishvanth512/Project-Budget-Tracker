class COCOMOCalculator:
    def __init__(self):
        self.scale_factors = {
            "Nominal": 1.0,
            "Very Low": 0.75,
            "Low": 0.88,
            "High": 1.15,
            "Very High": 1.4,
            "Extra High": 1.65
        }
        self.effort_multipliers = {
            "Nominal": 1.0,
            "Very Low": 0.75,
            "Low": 0.88,
            "High": 1.15,
            "Very High": 1.4,
            "Extra High": 1.65
        }

    def calculate_effort(self, sloc, reused, modified, scale_factors, effort_multipliers):
        """
        Calculate effort using COCOMO II formula.
        - sloc: Source Lines of Code (in thousands).
        - reused: Percentage of reused code.
        - modified: Percentage of modified code.
        - scale_factors: Dictionary of scale factors.
        - effort_multipliers: Dictionary of cost drivers.
        """
        kloc = sloc / 1000
        scale_factor_sum = sum(scale_factors.values())
        exponent = 0.91 + 0.01 * scale_factor_sum

        # Adjust for reused code
        adjusted_kloc = kloc * (1 - reused / 100 + 0.4 * reused / 100 * (modified / 100))

        # Calculate effort
        product_effort_multiplier = 1
        for multiplier in effort_multipliers.values():
            product_effort_multiplier *= multiplier

        effort = 2.94 * (adjusted_kloc ** exponent) * product_effort_multiplier
        return effort

    def calculate_schedule(self, effort):
        """
        Calculate the schedule (duration) in months.
        """
        schedule = 3.67 * (effort ** 0.28)
        return schedule