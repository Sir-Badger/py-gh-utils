# Util functions:
### download_files_gh
Given a repository, this function downloads files from the specified directory/directories within the repository. By default it downloads all files in a repository. It makes any needed subdirectories on the local filesystem, so that the target directory is equal to the source directory. 

If the files it wants to download have an equivalent of the same name on the local filesystem where it wants to save the file, it will check to see whether the github file or local file is more up to date. If the local file has been modified at a later date than the github file, it won't be downloaded (the local file is up to date).

**Parameters:**
- *repo*: a string representation of the repository
- *source*: a string or list of strings that describe the subdirectories/files in the repo to be downloaded
- *target*: a filepath on the local filesystem where the downloaded files will be stored. Defaults to the current path when the function is executed
- *exclude_files*: files with names equal to this parameter will be ignored. Can be a string or list of strings
- *exclude_dir*: directories with names equal to this parameter will be ignored, so their contents won't be downloaded. Can be a string or list of strings