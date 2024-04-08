from typing import Dict, List
import logging

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logging.getLogger("httpx").setLevel(logging.WARNING)
logger = logging.getLogger(__name__)

class Users:
    def __init__(self, allowed_users: str) -> None:
        users = allowed_users.split(',')
        self.users: Dict[int, List[str]] = {}
        [self._add_user(int(u)) for u in users]
    
    def _add_user(self, userid: str) -> None:
        if userid not in self.users:
            self.users[userid] = []
            logger.info(f"User '{userid}' added successfully.")
        else:
            logger.info(f"User '{userid}' already exists.")
            
    def is_user_exists(self, userid: str) -> bool:
        return self.users.__contains__(userid)
    
    def add_data(self, userid: str, data: str):
        if(not self.is_user_exists(userid)):
            logger.info(f"User '{userid}' not present in the system to add data.")
            return
        self.users.get(userid).append(data)
        
    def get_data(self, userid: str):
        if(not self.is_user_exists(userid)):
            logger.info(f"User '{userid}' not present in the system to add data.")
            return
        return self.users.get(userid)
    
    def clear_data(self, userid: str):
        if(not self.is_user_exists(userid)):
            logger.info(f"User '{userid}' not present in the system to clear data.")
            return
        self.users.get(userid).clear()