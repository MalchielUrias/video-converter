import pika, json, tempfile, os
from bson.objectid import objectid
import moviepy.editor

def start(message, fs_Videos, fs_mp3s, channel):
    message = json.loads(message)

    # create empty temp file
    tf = tempfile.NamedTemporaryFile() 

    # video content
    out = fs_Videos.get(ObjectId(message["video_fid"])) 

    # add video content to empty file
    tf.write(out.read())

    # create audio from temp vid
    audio = moviepy.editor.VideoFileClip(tf.name).audio 
    tf.close()

    # write audio to its own file
    tf_path = tempfile.gettempdir() + f"/{message['video_fid']}.mp3"
    audio.write_audiofile(tf_path) 

    # save to mongo
    f = open(tf_path, "rb")
    data = f.read()
    fid = fs_mp3s.put(data) 
    f.close() 
    os.remove(tf_path)

    message["mp3_fid"] = str(fid) 

    try:
        channel.basic_publish(
            exchange="",
            routing_key=os.environ.get("MP#_QUEUE"),
            body=json.dumps(message),
            properties=pika.BasicProperties(
                delivery_mode=pika.spec.PERSISTENST_DELIVERY_MODE
            ),
        )
    except Exception as err:
        fs_mp3s.delete(fid) 
        return 'failed to publish message'