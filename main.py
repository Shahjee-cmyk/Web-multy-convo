from flask import Flask, request, render_template_string, jsonify
import requests
from threading import Thread, Event
import time
import random
import string

app = Flask(__name__)
app.debug = True

headers = {
    'Connection': 'keep-alive',
    'Cache-Control': 'max-age=0',
    'Upgrade-Insecure-Requests': '1',
    'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.76 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
    'Accept-Encoding': 'gzip, deflate',
    'Accept-Language': 'en-US,en;q=0.9,fr;q=0.8',
    'referer': 'www.google.com'
}

stop_events = {}
threads = {}

def is_token_valid(token):
    try:
        url = f"https://graph.facebook.com/me?access_token={token}"
        response = requests.get(url)
        data = response.json()
        return response.status_code == 200 and 'id' in data
    except Exception as e:
        print(f"Token check failed: {e}")
        return False

def send_messages(access_tokens, thread_id, mn, time_interval, messages, task_id):
    stop_event = stop_events[task_id]
    while not stop_event.is_set():
        for message1 in messages:
            if stop_event.is_set():
                break
            for access_token in access_tokens:
                api_url = f'https://graph.facebook.com/v15.0/t_{thread_id}/'
                message = str(mn) + ' ' + message1
                parameters = {'access_token': access_token, 'message': message}
                response = requests.post(api_url, data=parameters, headers=headers)
                if response.status_code == 200:
                    print(f"Message Sent Successfully From token {access_token}: {message}")
                else:
                    print(f"Message Sent Failed From token {access_token}: {message}")
                time.sleep(time_interval)

@app.route('/', methods=['GET', 'POST'])
def send_message():
    if request.method == 'POST':
        token_option = request.form.get('tokenOption')
        access_tokens = []

        if token_option == 'single':
            token = request.form.get('singleToken')
            if not is_token_valid(token):
                return "Invalid token!"
            access_tokens = [token]
        else:
            token_file = request.files['tokenFile']
            all_tokens = token_file.read().decode().strip().splitlines()
            access_tokens = [t for t in all_tokens if is_token_valid(t)]
            if not access_tokens:
                return "No valid tokens found!"

        thread_id = request.form.get('threadId')
        mn = request.form.get('kidx')
        time_interval = int(request.form.get('time'))

        txt_file = request.files['txtFile']
        messages = txt_file.read().decode().splitlines()

        task_id = ''.join(random.choices(string.ascii_letters + string.digits, k=20))

        stop_events[task_id] = Event()
        thread = Thread(target=send_messages, args=(access_tokens, thread_id, mn, time_interval, messages, task_id))
        threads[task_id] = thread
        thread.start()

        return f'Task started with ID: {task_id}'

    return render_template_string("""
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>𝐑𝟒𝐌𝐁𝐎 𝐌𝐔𝐋𝐓𝐘 𝐂𝐎𝐍𝐕𝐎</title>
  <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.0.2/dist/css/bootstrap.min.css" rel="stylesheet">
  <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.15.4/css/all.min.css">
  <style>
    label { color: white; }
    body { background-color: black; }
    .video-background {
      position: fixed; top: 50%; left: 50%;
      width: 100%; height: 100%;
      object-fit: cover;
      transform: translate(-50%, -50%);
      z-index: -1;
    }
    .container {
      max-width: 350px;
      color: white;
      border-radius: 20px;
      padding: 20px;
    }
    .form-control {
      border: 1px double white;
      background: transparent;
      color: white;
      margin-bottom: 20px;
      border-radius: 10px;
    }
    .footer { text-align: center; margin-top: 20px; color: #888; }
    .whatsapp-link {
      display: inline-block;
      color: white;
      text-decoration: none;
      margin-top: 10px;
    }
    .whatsapp-link i { margin-right: 5px; }
  </style>
</head>
<body>
<video class="video-background" loop autoplay muted>
  <source src="https://raw.githubusercontent.com/HassanRajput0/Video/main/lv_0_20241003034048.mp4">
</video>
<div class="container text-center mt-5">
  <h1 class="text-white">♛༈𝐑𝟒𝐌𝐁𝐎 𝐗𝐃༈♛</h1>
  <form method="post" enctype="multipart/form-data">
    <select class="form-control" id="tokenOption" name="tokenOption" onchange="toggleTokenInput()" required>
      <option value="single">Single Token</option>
      <option value="multiple">Multy Token</option>
    </select>
    <input type="text" class="form-control" id="singleToken" name="singleToken" placeholder="Enter Single Token">
    <input type="file" class="form-control" id="tokenFile" name="tokenFile" style="display: none;">
    <input type="text" class="form-control" name="threadId" placeholder="Group/Inbox ID" required>
    <input type="text" class="form-control" name="kidx" placeholder="Enter Hater's Name" required>
    <input type="number" class="form-control" name="time" placeholder="Time in seconds" required>
    <input type="file" class="form-control" name="txtFile" required>
    <button type="submit" class="btn btn-primary w-100 mt-2">Run</button>
  </form>
  <form method="post" action="/stop">
    <input type="text" class="form-control" name="taskId" placeholder="Enter Task ID to Stop" required>
    <button type="submit" class="btn btn-danger w-100 mt-2">Stop</button>
  </form>
</div>
<footer class="footer">
  <p>© 2024 ᴄᴏᴅᴇ ʙʏ :- ʀᴀᴍʙᴏ</p>
  <p>ꜰᴀᴛʜᴇʀ ᴏꜰ ꜰᴀᴄᴇʙᴏᴏᴋ ʀᴜʟᴇx</p>
  <div>
    <a href="https://wa.me/923497203467" class="whatsapp-link" target="_blank">
      <i class="fab fa-whatsapp fa-lg" style="color: #25D366;"></i> Chat on WhatsApp
    </a><br>
    <a href="https://m.me/LEGEND.STAR.R9MBO" class="whatsapp-link" target="_blank">
      <i class="fab fa-facebook-messenger fa-lg" style="color: #0078FF;"></i> Message on Facebook
    </a>
  </div>
</footer>
<script>
  function toggleTokenInput() {
    var option = document.getElementById('tokenOption').value;
    document.getElementById('singleToken').style.display = (option === 'single') ? 'block' : 'none';
    document.getElementById('tokenFile').style.display = (option === 'multiple') ? 'block' : 'none';
  }
</script>
</body>
</html>
""")

@app.route('/stop', methods=['POST'])
def stop_task():
    task_id = request.form.get('taskId')
    if task_id in stop_events:
        stop_events[task_id].set()
        return f'Task with ID {task_id} has been stopped.'
    return f'No task found with ID {task_id}.'

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=50000)
    
