# coding=utf-8
import sys
import os
import os.path
import paramiko

def trans_file(ip, user, passwd, file, place):
  """
  :param ip: 目标服务器ip
  :param user: 目标服务器user
  :param paswd: 目标服务器user的password
  :param file: 需要传输的文件file
  :param place: 目标服务器的存放位置/文件 place/file
  :return: 是否传输成功
  """
  def printTotals(transferred, toBeTransferred):
      print "Transferred: {0}\tOut of: {1}".format(transferred, toBeTransferred)
  try:
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(ip, username=user, password=passwd)
    sftp = ssh.open_sftp()
    sftp.put('file', 'place',callback=printTotals)
    sftp.close()
    ssh.close()

  except Exception as e:
      return('*** Caught exception: %s: %s' % (e.__class__, e))


def run_cmd(ip, user, passwd, cmd):
    """
    :param ip: 目标服务器ip
    :param user: 目标服务器user
    :param paswd: 目标服务器user的password
    :param cmd: 目标服务器ip执行的命令
    :return: 执行的反馈
    """
    try:
      ssh = paramiko.SSHClient()
      ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
      ssh.connect(ip, username=user, password=passwd)
      stdin, stdout, stderr = ssh.exec_command(cmd)
      out = stdout.readlines()
      ssh.close()
      return out

    except Exception as e:
        return('*** Caught exception: %s: %s' % (e.__class__, e))
  
