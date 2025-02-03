import logging

def setup_logging():
    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s - %(levelname)s - %(message)s",
        handlers=[
            logging.FileHandler("app_debug.log"),
            logging.StreamHandler()
        ],
    )
    logging.info("Logging is set up.")