class MonetizationTier:
    FREE = "Explorer"
    PRO = "Analyst"
    ENTERPRISE = "Visionary"

    def __init__(self, current_tier: str = FREE):
        self.current_tier = current_tier

    def has_real_time_api(self):
        return self.current_tier in [self.PRO, self.ENTERPRISE]

    def has_alile_pay(self):
        return self.current_tier in [self.PRO, self.ENTERPRISE]

    def has_gemma_4_cv(self):
        return self.current_tier == self.ENTERPRISE

    def has_google_maps_premium(self):
        return self.current_tier == self.ENTERPRISE

    def get_max_local_llms(self):
        if self.current_tier == self.FREE:
            return 5 # Limit based on web/mobile capacity
        return 10
