import pika, sys, os, time
from pymongo import MongoClient
import gridfs
from convert import to_mp3

def main():
    client = MongoClient("host", 27017) # MongoDB host. Not to be deployed in cluster
    db_Videos = client.Videos
    db_mp3 = client.mp3s

    # gridfs
    fs_Videos = gridfs.GridFS(db_Videos)
    fs_mp3s = gridfs.GridFS(db_mp3) 

    # rabbitmq connection
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(host="rabbitmq") 
    )
    channel = connection.channel()

    # callback function
    def callback(c, method, properties, body):
        err = to_mp3.start(body, fs_Videos, fs_mp3s, ch) 
        if err:
            ch.basic_nack(delivery_tag=method.delivery_tag) 
        else:
            ch.basic_ack(delivery_tag=method.delivery_tag)


    channel.basic_consume(
        queue=os.environ.get("VIDEO_QUEUE"), on_message_callback=callback # consume messages from video queue
    )

    print("Waiting for messages. To exit press CTRL+C")

    channel.start_consuming()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("Interrupted")
        try:
            sys.exit(0)
        except SystemExit:
            os.exit(0) 