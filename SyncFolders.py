import sched,sys,os,shutil,time,logging
from datetime import datetime

def schedule_func(scheduler, interval, action, args=()):
    # # Remove any existing handlers that might have been added previously
    # for handler in logger.handlers[:]:
    #     logger.removeHandler(handler)
    scheduler.enter(interval, 1, schedule_func, (scheduler, interval, action, args))
    action(*args)

def checkValidDir(src):
    if os.path.isdir(src):
        return True
    return False

def sync_folders(src, dest,logger):   

    """
    Synchronizes two folders.
    """
    logger.info("Running synchronization between Source Folder: "+src+" and Destination Folder: "+dest)

    # Make sure source and destination are valid directories
    if not checkValidDir(src):
        logger.error(f"Source Folder: {src} is not a directory")
        logger.critical("Synchronization stopped due to unavailability of source directory. Process Stopped!")
        sys.exit("Exiting...")

    # Walk through the source directory
    for root, dirs, files in os.walk(src):

        # Get the corresponding destination directory
        dest_root = os.path.join(dest, os.path.relpath(root, src))
        
        if not checkValidDir(dest):
            logger.info(f"{dest} is not a directory. Creating a new {dest} directory")

        # Make sure the destination directory exists
        if not checkValidDir(dest_root):
            os.makedirs(dest_root)

        # Copy over new or updated files

        for file in files:
            src_file = os.path.join(root, file)
            dest_file = os.path.join(dest_root, file)

            # Only copy over the file if it doesn't exist or is newer in the source directory
            if not os.path.exists(dest_file) or os.path.getmtime(src_file) > os.path.getmtime(dest_file):
                logger.info(f"copying File: {file} to {os.path.dirname(dest_root)} folder")
                shutil.copy2(src_file, dest_file)
      
        for file in os.listdir(dest_root):
            dest_file = os.path.join(dest_root, file)

            # Delete any files that are in the destination but not in the source
            if os.path.isfile(dest_file) and file not in files:
                logger.info(f"removing File: {file} from {os.path.dirname(dest_root)} folder")
                os.remove(dest_file)

        # Delete any empty directories in the destination
        for dir in os.listdir(dest_root):
            dest_dir = os.path.join(dest_root, dir)
            if os.path.isdir(dest_dir) and not os.listdir(src):
                logger.info(f"removing {dir} from {os.path.dirname(dest_root)} folder")
                os.rmdir(dest_dir)

def createLogger(logFile):
    # Create a logger object
    logger = logging.getLogger("my_logger")
    logger.setLevel(logging.DEBUG)

    # Create a file handler and set its level to INFO
    file_handler = logging.FileHandler(logFile)
    file_handler.setLevel(logging.INFO)

    # Create a formatter and add it to the handler
    formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
    file_handler.setFormatter(formatter)

    # Add the handler to the logger
    logger.addHandler(file_handler)

    # Create a console handler and set its level to DEBUG
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.DEBUG)

    # Create a formatter and add it to the handler
    formatter = logging.Formatter("%(levelname)s - %(message)s")
    console_handler.setFormatter(formatter)

    # Add the handler to the logger
    logger.addHandler(console_handler)

    return logger


if __name__=="__main__":

    sourceFolder=sys.argv[1]
    destinationFolder=sys.argv[2]
    logInterval=float(sys.argv[3])
    logFile=sys.argv[4]
    
    # create a scheduler object
    scheduler = sched.scheduler(time.time, time.sleep)

    # schedule the execution of the function as per the logInterval argument
    schedule_func(scheduler, logInterval, sync_folders,[sourceFolder,destinationFolder,createLogger(logFile)])

    # start the scheduler
    scheduler.run()