# coding: utf-8
import piexif
from PIL import Image
import datetime, random, os, shutil, glob, multiprocessing, zipfile, json, hashlib

first_name = ["Sofia", "Julian", "Aidan", "Leah", "Harry", "Jake", "Evelyn", "Lucy", "Hayden", "Julia", "Savannah",
              "Jeremiah", "Luis", "Blake", "Sydney", "Dominic", "Chase", "Ellie", "Rachel", "Ruby", "Alexandra",
              "Lillian", "Katherine", "Peyton", "Allison", "Eric", "Sean", "Oscar", "Brooke", "Xavier"]

last_name = ["Aaron", "Abel", "Abraham", "Adam", "Adrian", "Alva", "Alex", "Alexander", "Alan", "Albert", "Alfred",
             "Andrew", "Andy", "Angus", "Anthony", "Arthur", "Austin", "Ben", "Benson", "Bill", "Bob", "Brandon",
             "Brant", "Brent", "Brian", "Bruce", "Carl", "Cary", "Caspar", "Charles", "Cheney", "Chris", "Christian",
             "Christopher", "Colin", "Cosmo", "Daniel", "Dennis", "Derek", "Donald", "Douglas", "David", "Denny",
             "Edgar", "Edward", "Edwin", "Elliott", "Elvis", "Eric", "Evan", "Francis", "Frank", "Franklin", "Fred",
             "Gabriel", "Gaby", "Garfield", "Gary", "Gavin", "George", "Gino", "Glen", "Glendon", "Harrison", "Hugo",
             "Hunk", "Howard", "Henry", "Ignativs", "Ivan", "Isaac", "Jack", "Jackson", "Jacob", "James", "Jason",
             "Jeffery", "Jerome", "Jerry", "Jesse", "Jim", "Jimmy", "Joe", "John", "Johnny", "Joseph", "Joshua",
             "Justin", "Keith", "Ken", "Kenneth", "Kenny", "Kevin", "Lance", "Larry", "Laurent", "Lawrence", "Leander",
             "Lee", "Leo", "Leonard", "Leopold", "Loren", "Lori", "Lorin", "Luke", "Marcus", "Marcy", "Mark", "Marks",
             "Mars", "Martin", "Matthew", "Michael", "Mike", "Neil", "Nicholas", "Oliver", "Oscar", "Paul", "Patrick",
             "Peter", "Philip", "Phoebe", "Quentin", "Randall", "Randolph", "Randy", "Reed", "Rex", "Richard", "Richie",
             "Robert", "Robin", "Robinson", "Rock", "Roger", "Roy", "Ryan", "Sam", "Sammy", "Samuel", "Scott", "Sean",
             "Shawn", "Sidney", "Simon", "Solomon", "Spark", "Spencer", "Spike", "Stanley", "Steven", "Stuart",
             "Terence", "Terry", "Timothy", "Tommy", "Tom", "Thomas", "Tony", "Tyler", "Van", "Vern", "Vernon",
             "Vincent", "Warren", "Wesley", "William"]


def failed_exit(ret: int, note: str):
    if ret:
        print("ERROR:  " + note)
        exit(1)


def random_str(type="name") -> str:
    """
    generate random str.
    :return: str
    """
    if type == "name":
        ran_str = ''.join(random.sample(first_name, 1)) + ' ' + ''.join(random.sample(last_name, 1))
    elif type == "key":
        ran_str = ''.join(random.sample(last_name,1)).lower() + ''.join(random.sample(last_name, 1)).lower()
    else:
        ran_str = ''.join(random.sample(["1", "2", "3", "4", "5", "6", "7", "8", "9"], 4))
    return ran_str


def get_file_path(root_dir='./', suffix='.png', condition: str or list = None, exclude: str or list = None) -> list:
    """
    return all eligible file's full path
    :param root_dir: the root directory where to search file.
    :param suffix: file type
    :param condition: str or list, file info for searching. str: signle condition, list: multi condition
    :param exclude: str or list, exclude file condition. str: signle condition, list: multi condition
    :return: list , all file's path that searching return.
    """
    res = list()
    cond = []
    excl = []

    def is_condition(cond, file) -> bool:
        for c in cond:
            if c.lower() in file:
                continue
            else:
                return False
        return True

    def is_exclude(exc, file) -> bool:
        for e in exc:
            if e.lower() in file:
                return False
        return True

    def get_file(root_dir: str, suffix: str, condition: list, exclude: list):
        for root, dirs, files in os.walk(root_dir):
            for file in files:
                tmp_file = os.path.join(root, file).lower()
                if os.path.splitext(file)[1] == suffix:
                    if is_condition(condition, tmp_file) and is_exclude(exclude, tmp_file):
                        res.append(os.path.join(root, file))

    if not condition:
        condition = suffix
    if not exclude:
        exclude = ' '
    if root_dir != './' and root_dir != '.':
        root_dir = root_dir.strip('./').lower()
        for root, dirs, files in os.walk('.'):
            if root.strip('./').lower() == root_dir:
                root_dir = root
                break
    if isinstance(condition, str):
        cond = [condition]
    elif isinstance(condition, list):
        cond = condition

    if isinstance(exclude, str):
        excl = [exclude]
    elif isinstance(exclude, list):
        excl = exclude

    if not isinstance(cond, list) or not isinstance(excl, list):
        print("Invalid condition format.")
        sys.exit(1)
    get_file(root_dir=root_dir, suffix=suffix, condition=cond, exclude=excl)
    return list(set(res))


#
# def update_exif(img_path: str) -> bool:
#     if(os.path.exists(img_path)):
#         try:
#             img = Image(filename=img_path)
#             timespan: str = str(datetime.datetime.now())
#             author: str = random_str()
#             exif: dict = {'Exif.Image.DateTime': str(timespan),
#                           'Exif.Photo.DateTimeOriginal': str(timespan),
#                           'Exif.Image.Artist': author}
#
#             xmp: dict = {'Xmp.xmp.CreateDate': str(timespan)}
#             img.modify_xmp(xmp)
#             img.modify_exif(exif)
#             img.close()
#         except:
#             return False
#     else:
#         return False
#     return True

def update_exif(img_path: str) -> bool:
    exif_dict = {
        piexif.ExifIFD.DateTimeOriginal: str(datetime.datetime.now()),
        piexif.ExifIFD.DateTimeDigitized: str(datetime.datetime.now()),
    }
    exif_bytes = piexif.dump({"Exif": exif_dict})
    if (os.path.exists(img_path)):
        try:
            img = Image.open(fp=img_path)
            img.save(img_path, exif=exif_bytes)
        except:
            return False
    else:
        return False
    return True


def find_specify_file(path: str, suffix: str) -> list:
    all = []
    ret = []
    for root, dirs, files in os.walk(path):
        for filespath in files:
            all.append(os.path.join(root, filespath))
    for i in all:
        if os.path.splitext(i)[1] == suffix:
            ret.append(i)
    return ret


def build_job(cmd: str):
    failed_exit(os.system(cmd), "Build " + cmd.split(' ')[1] + "failed.")


def async_do_job_list(args_list: list, process_num: int = 3):
    task_pool = multiprocessing.Pool(processes=process_num)
    for arg in args_list:
        task_pool.apply_async(func=build_job, args=(arg,))

    task_pool.close()
    task_pool.join()


def calc_file_md5(path: str) -> str or None:
    if os.path.exists(path) and os.path.isfile(path):
        with open(path, 'rb') as f:
            return hashlib.md5(f.read()).hexdigest().upper()
    return None


def update_config_hash(path: str, hash: str):
    for cfg in get_file_path(root_dir=path, suffix=".json"):
        cfg_json = {}
        with open(cfg, 'r') as rf:
            cfg_json = json.load(rf)
        plgs = cfg_json.get('plugins')
        if isinstance(plgs, list) and len(plgs) > 0:
            for plg in plgs:
                plg['hash'] = hash
            with open(cfg, 'w+') as wf:
                json.dump(cfg_json, wf)


def zip_files_cmp(path: str, out_dst: str, pwd: str or None):
    files = " "
    full_path = " "
    if os.path.isdir(path):
        files += " ".join(os.listdir(path))
        full_path = "cd " + path + " && "
    else:
        files += path
    if pwd:
        cmd = '%s zip -P %s -r %s  %s && mv %s %s/ ' % (
            full_path, pwd, out_dst, files, out_dst, os.getenv("WORKSPACE", "../"))
    else:
        cmd = '%s zip -r %s %s && mv %s %s/' % (full_path, out_dst, files, out_dst, os.getenv("WORKSPACE", "../"))
    os.system(cmd)


def rename_path(path: str, old_name: str, new_name: str):
    if not os.path.exists(path):
        return
    if old_name == new_name:
        return
    code_path = path + 'src/main/java/'
    old_path_name = old_name.replace('.','/')
    new_path_full = new_name.replace('.', '/')
    new_path_last = new_path_full.split('/')[-1]
    new_path_head = "/".join(new_path_full.split('/')[0:-1])
    if os.path.exists(code_path):
        shutil.move(code_path + old_path_name, new_path_last)
        shutil.rmtree(code_path + "com")
        os.makedirs(code_path + new_path_head)
        shutil.move(new_path_last, code_path + new_path_head)
        for java in get_file_path(root_dir=code_path, suffix='.java'):
            with open(java, 'r') as rf:
                lines = rf.readlines()
            with open(java, 'w+', encoding='utf-8') as wf:
                for line in lines:
                    if not line:
                        continue
                    if old_name in line:
                        line = line.replace(old_name, new_name)
                    wf.write(line)
    with open(path + 'build.gradle', 'r') as rf:
        lines = rf.readlines()
    with open(path + 'build.gradle', 'w+') as wf:
        for line in lines:
            if not line:
                continue
            if 'applicationId' in line and old_name in line:
                line = line.replace(old_name, new_name)
            wf.write(line)
    for file in get_file_path(root_dir=path, suffix='.xml', condition="AndroidManifest"):
        with open(file, 'r') as rf:
            lines = rf.readlines()
        with open(file, 'w+', encoding='utf-8') as wf:
            for line in lines:
                if not line:
                    continue
                if old_name in line:
                    line = line.replace(old_name, new_name)
                wf.write(line)


def update_value_by_cond(root_path: str, match_name: str or None, suff: str, cond: str, old_val: str, new_val: str):
    if old_val == new_val:
        return
    for file in get_file_path(root_dir=root_path, suffix=suff, condition=match_name):
        with open(file, 'r') as rf:
            lines = rf.readlines()
        with open(file, 'w+', encoding='utf-8') as wf:
            for line in lines:
                if not line:
                    continue
                if cond in line and old_val in line:
                    line = line.replace(old_val, new_val)
                wf.write(line)


def replace_proj_res(src: str):
    print("replace proj: " + src)
    res_path = 'Banana/app/src/main/res'
    test_path = 'Banana/app/src/main/assets/test'
    if os.path.exists(src + '/res'):
        shutil.rmtree(res_path)
        shutil.move(src + '/res', res_path)
    if os.path.exists(src + '/test'):
        os.remove(test_path)
        shutil.copy2(src + '/test', test_path)


def replace_ssl_content(ssl_url:None or str,src_file:str):
    ssl_file = "ssl.txt"
    ssl_ctx = str()
    if ssl_url is None:
        return
    else:
        failed_exit(os.system("curl -sSL %s -o %s"%(ssl_url,ssl_file)),"Get ssl file failed.")
        failed_exit(os.system("sed -e 's/^/\"&/g' -i %s" % ssl_file),"modify ssl file failed.")
        failed_exit(os.system("sed -e 's/$/\\\n\" +/g' -i %s"  % ssl_file),"modify ssl file failed.")
        failed_exit(os.system("sed -e 's/END CER.*$/END CERTIFICATE-----\";/g' -i %s " % ssl_file), "modify ssl file failed.")
    with open(file=ssl_file,mode='r',encoding="utf-8") as new_ssl_fd:
        ssl_ctx = new_ssl_fd.read()
    with open(file=src_file,mode='r',encoding='utf-8') as rf:
        lines = rf.readlines()
    with open(file=src_file,mode='w+',encoding='utf-8') as wf:
        for line in lines:
            print(line)
            if not line:
                continue
            if "-----BEGIN" in line:
                line=""
            if '\\n" +' in line:
                line=""
            if '-----END' in line:
                line=ssl_ctx
            wf.write(line)

# Banana\app\src\main\java\com

if __name__ == "__main__":
    #
    # init environment
    proj = os.getenv('project', 'jz')

    old_app_name_dict = {'jz': "橘子影视", 'dxj': "大香蕉", 'xyj': "小妖精", 'zd': '遮挡'}
    old_path_name = "com.xinjuzi.app"
    old_version_code = "66"
    old_version_name = "v1.6.6"
    old_package_version = "34"
    old_api_addr_dict = {'jz': "https://juzi-api.jxkuaibu.cn/", 'dxj': "https://dxj-api.jxkuaibu.cn/", 'xyj': 'https://api.ccyc.net.cn/',
                         'zd': 'https://zhedang-api.jxkuaibu.cn/'}
    old_api_planb_addr_dict = {'jz': "http://juzi-api.jsykgc.com:81/", 'dxj': "http://dxj-api.jsykgc.com:81/", 'xyj': 'http://xyj-api.jsykgc.com:81/',
                         'zd': 'http://zhedang-api.jsykgc.com:81/'}
    old_api_addr = old_api_addr_dict.get(proj)
    old_api_planb_addr = old_api_planb_addr_dict.get(proj)
    old_app_name = old_app_name_dict.get(proj)
    old_random_key = "random_key_for_xml_id"

    zip_dir = "./plugin"
    key_store = "test.keystore"
    plugin_shadow_md5 = str()
    # zip_pwd = random_str("pwd")
    zip_pwd = None if len(os.getenv("zipPassword", "")) < 1 else os.getenv("zipPassword", "")
    job_name = os.getenv("JOB_BASE_NAME", "app")
    new_path_name = old_path_name if len(os.getenv("pathName", "")) < 1 else os.getenv("pathName")
    new_version_code = os.getenv("versionCode", old_version_code)
    new_version_name = os.getenv("versionName", old_version_name)
    new_package_version = os.getenv("packageVersion", old_package_version)
    new_api_addr = old_api_addr if len(os.getenv("apiAddress", "")) < 1 else os.getenv("apiAddress")
    new_api_planb_addr = old_api_planb_addr if len(os.getenv("apiAddressPlanB","")) < 1 else os.getenv("apiAddressPlanB")
    new_app_name = os.getenv("appName", old_app_name)
    ssl_url = None if len(os.getenv("sslUrl","")) < 1 else os.getenv("sslUrl")
    sign_url = None if len(os.getenv("signUrl","")) < 1 else os.getenv("signUrl")
    sign_pwd = None
    sign_name = None
    if sign_url:
        sign_pwd = None if len(os.getenv("signPwd","")) < 1 else os.getenv("signPwd")
        sign_name = None if len(os.getenv("signName","")) < 1 else os.getenv("signName")
        if sign_pwd is None or sign_name is None:
            print("Error: signPwd or signName not match.")
            exit(1)
    # replace file
    # replace_proj_res(src="replace_files/"+proj)

    # modify specify value by key.
    update_value_by_cond(root_path="./Banana/app/src/", match_name="strings", suff=".xml", cond="app_name",
                         old_val=old_app_name, new_val=new_app_name)

    update_value_by_cond(root_path="./Banana/app/src/", match_name=None, suff=".xml", cond=old_random_key,
                         old_val=old_random_key, new_val=old_random_key+random_str("key"))

    update_value_by_cond(root_path="./Banana/app/src/main/java", match_name=None, suff=".java", cond="raw_domain_bak",
                         old_val=old_api_planb_addr, new_val=new_api_planb_addr)

    for file in get_file_path(root_dir="./Banana/app/src/main/java",suffix=".java",condition="SSLContextHelper"):
        replace_ssl_content(ssl_url=ssl_url,src_file=file)

    for file in get_file_path(root_dir="./BananaPlugin/plugin/src/main/java/com",suffix='.java',condition='SSLContextHelper'):
        replace_ssl_content(ssl_url=ssl_url,src_file=file)

    update_value_by_cond(root_path="./", match_name=None, suff=".java", cond="https", old_val=old_api_addr,
                         new_val=new_api_addr)

    update_value_by_cond(root_path="./", match_name=None, suff=".properties", cond="https", old_val=old_api_addr,
                         new_val=new_api_addr)

    update_value_by_cond(root_path="Banana/", match_name="build", suff=".gradle", cond="versionCode",
                         old_val=old_version_code,
                         new_val=new_version_code)

    update_value_by_cond(root_path="Banana/", match_name="build", suff=".gradle", cond="versionName",
                         old_val=old_version_name,
                         new_val=new_version_name)

    update_value_by_cond(root_path="Banana/app/src/", match_name="HttpUtils", suff=".java", cond="package-version",
                         old_val=old_package_version, new_val=new_package_version)

    rename_path(path="Banana/app/", old_name=old_path_name, new_name=new_path_name)

    update_value_by_cond(root_path="BananaPlugin/", match_name="build", suff=".gradle", cond="versionCode",
                         old_val=old_version_code,
                         new_val=new_version_code)

    update_value_by_cond(root_path="BananaPlugin/", match_name="build", suff=".gradle", cond="versionName",
                         old_val=old_version_name,
                         new_val=new_version_name)

    rename_path(path="BananaPlugin/app/", old_name=old_path_name, new_name=new_path_name)
    rename_path(path="BananaPlugin/plugin-shadow-apk/", old_name=old_path_name, new_name=new_path_name)

    # update exif all PNG image.
    for img_path in get_file_path(root_dir="./", suffix=".png"):
        if update_exif(img_path=img_path):
            print("Modify image's EXIF date:" + img_path)
            pass
        else:
            print("Failed: update image " + img_path)
    for apk in glob.glob("./*.apk"):
        os.remove(apk)

    # generate apk.
    failed_exit(os.system("cd BananaPluginManager && ./gradlew build -d -q --parallel -p app "),
                "Build BananaPluginManager failed.")
    for apk in get_file_path(root_dir="./BananaPluginManager", suffix=".apk", condition="debug"):
        shutil.copy2(apk, "Banana/app/src/main/assets/")

    args = ["cd Banana && ./gradlew build -d -q --parallel -p app",
            "cd BananaPlugin && ./gradlew build -d -q --parallel -p plugin-shadow-apk"]
    async_do_job_list(args_list=args)

    for apk in get_file_path(root_dir="./Banana/app", suffix=".apk", condition=["outputs", "release"]):
        failed_exit(os.system('echo "Signer Apk: %s"' % (apk)), "echo failed.")
        cmd =""
        if sign_url:
            os.remove(key_store)
            failed_exit(os.system("curl -sSL %s -o %s"%(sign_url,key_store)),"Get keystore file failed.")
            cmd = 'jarsigner -verbose -tsa http://sha256timestamp.ws.symantec.com/sha256/timestamp  -keystore %s -storepass %s -digestalg SHA1 -sigalg MD5withRSA %s "%s" > /dev/null' % (key_store,sign_pwd,apk,sign_name)
        else:
            cmd = 'jarsigner -verbose -tsa http://sha256timestamp.ws.symantec.com/sha256/timestamp  -keystore %s -storepass wiqun408 -digestalg SHA1 -sigalg MD5withRSA %s "loumi" > /dev/null' % (key_store,apk)
        failed_exit(os.system(cmd),
                    "Signer failed.")
        failed_exit(os.system('zipalign -v 1 %s %s.apk' % (apk, job_name)), "zipalign failed.")

    if os.path.exists(path=zip_dir):
        shutil.rmtree(path=zip_dir)
    z = zipfile.ZipFile(file="./34.zip", mode='r')
    z.extractall(path=zip_dir)
    z.close()

    for apk in get_file_path(root_dir="./BananaPlugin", suffix=".apk", condition=["debug", "shadow"]):
        failed_exit(os.system('echo "Move Apk: %s"' % (apk)), "echo failed.")
        plugin_shadow_md5 = calc_file_md5(path="plugin-shadow-apk-debug.apk")
        shutil.copy2(apk, "plugin")

    update_config_hash(path="plugin", hash=plugin_shadow_md5)

    zip_files_cmp(path=zip_dir, out_dst="plugin.zip", pwd=zip_pwd)
    zip_files_cmp(path="%s.apk" % (job_name), out_dst="%s.zip" % (job_name), pwd=zip_pwd)
    if zip_pwd:
        os.system('echo "The decrypt password:  %s " ' % zip_pwd)
        os.system("touch zip_pwd_%s" % zip_pwd)
    else:
        print("No password for zip file.")
