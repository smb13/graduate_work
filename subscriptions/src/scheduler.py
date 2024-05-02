import asyncio
import contextlib

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from jobs.subscriptions_renewal import subscriptions_renewal_job


def main() -> None:
    scheduler = AsyncIOScheduler()
    scheduler.add_job(
        subscriptions_renewal_job,
        CronTrigger.from_crontab("0 15 * * *"),
    )
    scheduler.start()

    with contextlib.suppress(KeyboardInterrupt, SystemExit):
        asyncio.get_event_loop().run_forever()


if __name__ == "__main__":
    main()
