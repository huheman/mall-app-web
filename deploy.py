import subprocess
import os

# 执行命令函数
def run_command(command):
    try:
        result = subprocess.run(command, shell=True, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        print(command,' ok')
    except subprocess.CalledProcessError as e:
        print(f"命令执行出错: {e.stderr.decode()}")
        raise

def main():
    # 打印 'hello'
    run_command("echo 'hello'")

    # 发布 H5 平台
    run_command("cli publish --platform h5 --project mall-app-web")

    # 远程删除文件夹下的内容，如果文件夹存在
    ssh_rm_command = "ssh root@192.168.1.34 \"rm -fr /root/env_dev/nginx/html/mall\""
    run_command(ssh_rm_command)

    # 使用 SCP 上传文件
    scp_command = "scp -r D:/project/page/mall-app-web/unpackage/dist/build/web/ root@192.168.1.34:/root/env_dev/nginx/html/mall/"
    run_command(scp_command)

    print("部署完成！")

if __name__ == "__main__":
    main()
