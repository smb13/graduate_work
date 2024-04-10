import backoff
from process.extract import RabbitMQExtractor, consuming_messages
from process.load import NotificationLoader
from process.transform import DataTransform
from store.rabbitmq.consumer import RabbitMQConsumer
from store.rabbitmq.publisher import RabbitMQPublisher

from core.config import rabbitmq_settings, settings
from core.logger import logger

dead_letters = []


@backoff.on_exception(backoff.expo, Exception, logger=logger, max_tries=settings.backoff_max_tries)
def main() -> None:
    logger.info(f"Start worker for {rabbitmq_settings.consume_queue} queue...")

    queue = rabbitmq_settings.consume_queue
    consumer = RabbitMQConsumer(queue=queue, routing_key=queue, consuming_messages=consuming_messages)
    publisher = RabbitMQPublisher(queue=queue.split(".")[0] + rabbitmq_settings.publish_queue_suffix)

    load = NotificationLoader().run(publisher, consumer)
    transform = DataTransform().run(next_node=load)
    extract = RabbitMQExtractor().run(next_node=transform)

    consumer.start()
    publisher.start()

    while True:
        try:
            messages = []
            while len(consuming_messages) == 0:
                pass
            while len(consuming_messages) > 0:
                messages.append(consuming_messages.pop())
            extract.send(messages)
        except Exception as exc:
            logger.warning(exc)
            consumer.stop()
            publisher.stop()
            raise Exception


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        logger.info("User terminated the process")
