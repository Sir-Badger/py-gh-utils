import os, urllib3, time
from github import Github
from github.Repository import Repository
from github.ContentFile import ContentFile

def _get_gh_files(repo: str | Repository, source: str | list[str] = "",
                 exclude_files: str | list[str] = [], exclude_dirs: str | list[str] = []) -> list[ContentFile]:
    if type(repo) == str: # get repo if needed
        with Github() as gh: repo = gh.get_repo(repo)
    # wrap singel excludes so they're always a list but you can input a string
    if exclude_files and type(exclude_files) == str: exclude_files = [exclude_files]
    if exclude_dirs and type(exclude_dirs) == str: exclude_dirs = [exclude_dirs]


    if type(source) == str: # single file/directory
        contents = repo.get_contents(source) # retrieve contents
        if type(contents) == ContentFile: return [contents] # single file

        files = []
        while contents:
            file_content = contents.pop(0)
            if file_content.type == "dir":
                if file_content.name in exclude_dirs: continue
                contents.extend(repo.get_contents(file_content.path))
            else:
                if file_content.name in exclude_files: continue
                files.append(file_content)
        return files
    else: # a list of files
        contents = [repo.get_contents(f) for f in source]
        return contents

def _download_gh_file(gh_file: ContentFile, target_path: str = os.getcwd(),
                     target_file: str = None):
    download_str = f'Downloading {gh_file.git_url} . . .'
    print(download_str, end="\r")

    if not target_file: target_file = gh_file.name
    if gh_file.name != gh_file.path:
        target_path = os.path.join(target_path, gh_file.path.removesuffix(gh_file.name))
    
    # if the target dir doesn't exist, create it
    if not os.path.exists(target_path):
        os.makedirs(target_path)

    with open(os.path.join(target_path, target_file), "wb") as file:
        http = urllib3.PoolManager()
        raw_file = http.request("GET", gh_file.download_url)
        file.write(raw_file.data)

    print(' '.join(['' for i in range(len(download_str)+1)]), end="\r") # clear last line
    print(f"Done. | {os.path.join(target_path, target_file)}")

def download_files_gh(repo: str | Repository, source: str | list[str] = "", target:str= os.getcwd(),
                 exclude_files: str | list[str] = [], exclude_dirs: str | list[str] = []) -> list[ContentFile]:
    if type(repo) == str: # get repo if needed
        with Github() as gh: repo = gh.get_repo(repo)
    
    print("Checking repo for updates/files to download ...")
    files = _get_gh_files(repo, source, exclude_files, exclude_dirs) # data
    files.extend(_get_gh_files(repo, "search")) # search
    
    files_to_update = []
    while files:
        file = files.pop(0)

        target_file = os.path.join(target, file.path)
        if os.path.exists(target_file):
            gh_mod_t_obj = time.strptime(file.last_modified, "%a, %d %b %Y %H:%M:%S %Z")
            gh_mod_unix = time.mktime(gh_mod_t_obj)
            if os.path.getmtime(target) < gh_mod_unix:
                files_to_update.append(file)
        else:
            files_to_update.append(file)
    
    print(f"{len(files_to_update)} files to update/download")
    if len(files_to_update) > 0:
        print("Updating/downloading files:")
        update_start_time = time.time()
        for file in files_to_update:
            _download_gh_file(file, target)
        print(f"Finished in {time.time() - update_start_time} seconds")
