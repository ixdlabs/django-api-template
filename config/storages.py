from datetime import datetime, timedelta, timezone

from storages.backends.azure_storage import AzureStorage


class CustomAzureStorage(AzureStorage):
    def _expire_at(self, expire):
        if expire < 3600:
            return super()._expire_at(expire)

        # If the expiration time is more than 1 hour, we cap the expiration to UTC hour + 1 time
        # to make sure the URL will be the same within the same hour
        time_after_hour = datetime.now(timezone.utc) + timedelta(hours=1)
        return time_after_hour.replace(minute=0, second=0, microsecond=0)
