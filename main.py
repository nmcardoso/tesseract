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

def get_last_uid():
  return int(subprocess.check_output(['tail', '-1', 'uid.log']))

def write_log(path, content):
  with open(path, 'a') as file:
    file.write('%s\n' % content)

def write_time_log(quantity, time):
  time_log = '%s follows in %s seconds with %s DELAY_BETWEEN and %s DELAY_END' \
              % (quantity, time, DELAY_BETWEEN, DELAY_END)
  write_log('time.log', time_log)

def determined_iteration(cookies, uid_start, uid_end):
  start_time = time.time()

  for uid in range(uid_start, uid_end + 1):
    current = uid - uid_start + 1
    remaining = uid_end - uid

    follow_resp = send_api_request(cookies, str(uid), 'follow')
    if (follow_resp.json()['msg'] == 'success'):
      print_status(current, uid, True)
    else:
      print('Error! Response: %s' % follow_resp.text)

    #time.sleep(0.0 + (random.random() * 0.5))
    time.sleep(DELAY_BETWEEN)

    unfollow_resp = send_api_request(cookies, str(uid), 'unfollow')
    if (unfollow_resp.json()['msg'] == 'success'):
      write_log('uid.log', str(uid))
      print_status(current, uid, True, True)
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
  current = 1
  uid = uid_start
  start_time = time.time()

  try:
    while(True):
      follow_resp = send_api_request(cookies, str(uid), 'follow')
      if (follow_resp.json()['msg'] == 'success'):
        print_status(current, uid, True)
      else:
        print('Error! Response: %s' % follow_resp.text)

      time.sleep(DELAY_BETWEEN)

      unfollow_resp = send_api_request(cookies, str(uid), 'unfollow')
      if (unfollow_resp.json()['msg'] == 'success'):
        write_log('uid.log', str(uid))
        print_status(current, uid, True, True)
      else:
        print('Error! Response: %s' % follow_resp.text)

      time.sleep(DELAY_END)
      current += 1
      uid += 1
  except KeyboardInterrupt:
    end_time = time.time()
    time_log = '%s follows in %s seconds with %s DELAY_BETWEEN and %s DELAY_END' \
              % (current, (end_time - start_time), DELAY_BETWEEN, DELAY_END)
    write_log('time.log', time_log)
    print('Execution time: %s' % (end_time - start_time))

def get_args():
  parser = argparse.ArgumentParser(description='Follows multiplier')
  parser.add_argument('-a', '--auto', action='store_true', 
                      help='''Start iterarions automatically without changing 
                              a range of ids inside uid.txt''')
  parser.add_argument('-q', nargs=1, type=int, 
                      help='''Quantity of follows requests, starting with 
                              the value inside uid.log + 1''')
  parser.add_argument('-t', '--time', nargs=1, type=int,
                      help='Delay time (in ms) for both delays')
  parser.add_argument('-b', '--time-between', nargs=1, type=int,
                      help='Delay time (in ms) between follow and unfollow')
  parser.add_argument('-e', '--time-end', nargs=1, type=int,
                      help='Delay time (in ms) after unfollow')
  return parser.parse_args()

def print_status(n, uid, follow=False, unfollow=False):
  bold = '\033[1m'
  green = '\033[1;32m'
  blue = '\033[34m'
  yellow = '\033[33m'
  ret = '\033[0m'
  check = '\u2714'
  if(follow and unfollow):
    print(f'[{green}#{n}{ret}]\t{bold}ID:{ret}{uid}\t{blue}{check} Follow{ret}\t{yellow}{check} Unfollow{ret}')
  elif (follow):
    print(f'[{green}#{n}{ret}]\t{bold}ID:{ret}{uid}\t{blue}{check} Follow{ret}', end='\r')
  return

def main():
  args = get_args()
  cookies = get_file_content('cookies.txt')
  attempt = 1
  max_attempts = 11
  global DELAY_BETWEEN
  global DELAY_END

  if (args.time):
    DELAY_BETWEEN = args.time[0] / 1000
    DELAY_END = args.time[0] / 1000
  else:
    if (args.time_between):
      DELAY_BETWEEN = args.time_between[0] / 1000
    if (args.time_end):
      DELAY_END = args.time_end[0] / 1000

  if (args.auto):
    if (not args.q):
      try:
        undetermined_iteration(cookies, get_last_uid() + 1)
      finally:
        if (attempt < max_attempts):
          attempt += 1
          undetermined_iteration(cookies, get_last_uid() + 1)
    else:
      determined_iteration(cookies, (get_last_uid() + 1), (get_last_uid() + args.q[0]))
  else:
    uid_range = get_file_lines('uid.txt')
    uid_start = int(uid_range[0])
    uid_end = int(uid_range[1])

if __name__ == '__main__':
  main()
