import asyncio
import contextlib

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from jobs.check_pending_payments import check_pending_job
from jobs.process_recurring_payments import process_recurring_job


def main() -> None:
    scheduler = AsyncIOScheduler()
    scheduler.add_job(
        process_recurring_job,
        CronTrigger.from_crontab("* * * * *"),
    )
    scheduler.add_job(
        check_pending_job,
        CronTrigger.from_crontab("* * * * *"),
    )
    scheduler.start()

    with contextlib.suppress(KeyboardInterrupt, SystemExit):
        asyncio.get_event_loop().run_forever()


if __name__ == "__main__":
    main()
