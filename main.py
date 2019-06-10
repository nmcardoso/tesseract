import requests
import time
import random
import argparse
import subprocess

API_BASE = 'https://www.cube.tv/userCenter'
DELAY_BETWEEN = 0.05
DELAY_END = 0.1

def send_api_request(cookies, uid, path):
  url = '%s/%s' % (API_BASE, path)
  headers = {
    'accept': 'application/json, text/plain, */*',
    'content-type': 'application/x-www-form-urlencoded',
    'origin': 'https://www.cube.tv',
    'referer': 'https://www.cube.tv/Weedzao',
    'user-agent': 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US) AppleWebKit/525.19 (KHTML, like Gecko) Chrome/1.0.154.53 Safari/525.19',
    'cookie': cookies
  }
  body = {
    'uid': uid
  }

  r = requests.post(url, data=body, headers=headers)

  return r

def get_file_content(path):
  data = None
  with open(path, 'r') as file:
    data = file.read().replace('\n', '')

  return data

def get_file_lines(path):
  data = None
  with open(path, 'r') as file:
    data = [line.strip() for line in file]

  return data

def write_log(path, content):
  with open(path, 'a') as file:
    file.write('%s\n' % content)

def determined_iteration(cookies, uid_start, uid_end):
  start_time = time.time()

  for uid in range(uid_start, uid_end + 1):
    current = uid - uid_start + 1
    remaining = uid_end - uid

    follow_resp = send_api_request(cookies, str(uid), 'follow')
    if (follow_resp.json()['msg'] == 'success'):
      print('User %d followed' % uid)
    else:
      print('Error! Response: %s' % follow_resp.text)

    #time.sleep(0.0 + (random.random() * 0.5))
    time.sleep(DELAY_BETWEEN)

    unfollow_resp = send_api_request(cookies, str(uid), 'unfollow')
    if (unfollow_resp.json()['msg'] == 'success'):
      write_log('uid.log', str(uid))
      print('User %d unfollowed' % uid)
    else:
      print('Error! Response: %s' % unfollow_resp.text)

    print('%d follows completed, %d remaining' % (current, remaining))
    
    if (remaining > 0):
      #time.sleep(0.0 + (random.random() * 0.5))
      time.sleep(DELAY_END)

  end_time = time.time()
  time_log = '%s follows in %s seconds with %s DELAY_BETWEEN and %s DELAY_END' \
              % ((uid_end - uid_start + 1), (end_time - start_time), 
              DELAY_BETWEEN, DELAY_END)
  write_log('time.log', time_log)
  print('Execution time: %s' % (end_time - start_time))

def undetermined_iteration(cookies, uid_start):
  current = 0
  uid = uid_start

  while(True):
    follow_resp = send_api_request(cookies, str(uid), 'follow')
    if (follow_resp.json()['msg'] == 'success'):
      print('User %d followed' % uid)
    else:
      print('Error! Response: %s' % follow_resp.text)

    time.sleep(DELAY_BETWEEN)

    unfollow_resp = send_api_request(cookies, str(uid), 'unfollow')
    if (unfollow_resp.json()['msg'] == 'success'):
      write_log('uid.log', str(uid))
      print('User %d unfollowed' % uid)
    else:
      print('Error! Response: %s' % follow_resp.text)

    print('%d follows completed' % current, remaining)
    time.sleep(DELAY_END)
    current += 1
    uid += 1

def get_args():
  parser = argparse.ArgumentParser(description='Follows multiplier')
  parser.add_argument('-a', '--auto', action='store_true', 
                      help='''Start iterarions automatically without changing 
                              a range of ids inside uid.txt''')
  parser.add_argument('-q', nargs=1, type=int, 
                      help='''Quantity of follows requests, starting with 
                              the value inside uid.log + 1''')
  return parser.parse_args()

def main():
  args = get_args()
  cookies = get_file_content('cookies.txt')

  if (args.auto):
    last_uid = int(subprocess.check_output(['tail', '-1', 'uid.log']))

    if (not args.q):
      undetermined_iteration(cookies, last_uid + 1)
    else:
      determined_iteration(cookies, (last_uid + 1), (last_uid + args.q[0]))
  else:
    uid_range = get_file_lines('uid.txt')
    uid_start = int(uid_range[0])
    uid_end = int(uid_range[1])

if __name__ == '__main__':
  main()
