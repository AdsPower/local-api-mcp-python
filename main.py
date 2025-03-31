from typing import Any, List, Optional, Dict, TypedDict, Literal, Union
import httpx
from mcp.server.fastmcp import FastMCP

# Initialize FastMCP server
mcp = FastMCP("adspower-local-api")

# Constants
LOCAL_API_BASE = "http://127.0.0.1:50325"

# 定义代理配置的类型
class ProxyConfig(TypedDict):
    proxy_soft: str  # ['brightdata', 'brightauto', 'oxylabsauto', '922S5auto', 'ipideeauto', 'ipfoxyauto', '922S5auth', 'kookauto', 'ssh', 'other', 'no_proxy']
    proxy_type: Optional[str]  # ['http', 'https', 'socks5', 'no_proxy']
    proxy_host: Optional[str]  # e.g., "127.0.0.1"
    proxy_port: Optional[str]  # e.g., "8080"
    proxy_user: Optional[str]  # proxy username
    proxy_password: Optional[str]  # proxy password
    proxy_url: Optional[str]  # e.g., "http://127.0.0.1:8080"
    global_config: Optional[str]  # "0" or "1", default is "0"

# 定义浏览器内核配置类型
class BrowserKernelConfig(TypedDict, total=False):
    version: Union[Literal["92"], Literal["99"], Literal["102"], Literal["105"], 
                  Literal["108"], Literal["111"], Literal["114"], Literal["115"], 
                  Literal["116"], Literal["117"], Literal["118"], Literal["119"], 
                  Literal["120"], Literal["121"], Literal["122"], Literal["123"], 
                  Literal["124"], Literal["125"], Literal["126"], Literal["127"], 
                  Literal["128"], Literal["129"], Literal["130"], Literal["131"], 
                  Literal["132"], Literal["133"], Literal["134"], Literal["ua_auto"]]  # default is "ua_auto"
    type: Literal["chrome", "firefox"]  # default is "chrome"

# 定义随机 UA 配置类型
class RandomUaConfig(TypedDict, total=False):
    ua_version: List[str]
    ua_system_version: List[Literal[
        "Android 9", "Android 10", "Android 11", "Android 12", "Android 13",
        "iOS 14", "iOS 15",
        "Windows 7", "Windows 8", "Windows 10", "Windows 11",
        "Mac OS X 10", "Mac OS X 11", "Mac OS X 12", "Mac OS X 13",
        "Linux"
    ]]

# 定义指纹配置类型
class FingerprintConfig(TypedDict, total=False):
    automatic_timezone: Literal["0", "1"]  # default is "0"
    timezone: str  # e.g., "Asia/Shanghai"
    language: List[str]  # e.g., ["en-US", "zh-CN"]
    flash: Literal["block", "allow"]
    fonts: List[str]  # e.g., ["Arial", "Times New Roman"]
    webrtc: Literal["disabled", "forward", "proxy", "local"]
    browser_kernel_config: BrowserKernelConfig
    random_ua: RandomUaConfig
    tls_switch: Literal["0", "1"]
    tls: str  # TLS configuration string

API_ENDPOINTS = {
    "start_browser": '/api/v1/browser/start',
    "close_browser": '/api/v1/browser/stop',
    "create_browser": '/api/v1/user/create',
    "get_browser_list": '/api/v1/user/list',
    "get_group_list": '/api/v1/group/list',
    "get_application_list": '/api/v1/application/list',
    "update_browser": '/api/v1/user/update',
    "delete_browser": '/api/v1/user/delete',
    "get_opened_browser": '/api/v1/browser/local-active',
    "create_group": '/api/v1/group/create',
    "update_group": '/api/v1/group/update',
    "move_browser": '/api/v1/user/regroup'
}

@mcp.tool()
def start_browser(browser_id: str = None, serial_number: str = None, ip_tab: str = None, launch_args: str = None, clear_cache_after_closing: bool = None, cdp_mask: str = None) -> str:
    """
    Start a browser with the Browser ID or Serial Number. Must provide one of the two.
    """
    params = {}
    if browser_id:
        params["user_id"] = browser_id
    elif serial_number:
        params["serial_number"] = serial_number
    if ip_tab:
        params["open_tabs"] = ip_tab
    if launch_args:
        params["launch_args"] = launch_args
    if clear_cache_after_closing is not None:
        params["clear_cache_after_closing"] = str(clear_cache_after_closing)
    if cdp_mask:
        params["cdp_mask"] = cdp_mask
    params["open_tabs"] = "0"

    response = httpx.get(f"{LOCAL_API_BASE}{API_ENDPOINTS['start_browser']}", params=params)
    if response.status_code == 200:
        data = response.json()
        if data["code"] == 0:
            formatted_data = '\n'.join(f"{key}: {value}" for key, value in data['data'].items())
            return f"Browser opened successfully with:\n{formatted_data}"
        else:
            return f"Failed to start browser, error: {data['msg']}"
    else:
        return f"Failed to start browser, error: {response.text}"

@mcp.tool()
def close_browser(browser_id: str) -> str:
    """
    Close a browser with the Browser ID.
    """
    response = httpx.get(f"{LOCAL_API_BASE}{API_ENDPOINTS['close_browser']}", params={"user_id": browser_id})
    if response.status_code == 200:
        data = response.json()
        if data["code"] == 0:
            return f"Browser {browser_id} closed successfully"
        else:
            return f"Failed to close browser {browser_id}, error: {data['msg']}"
    else:
        return f"Failed to close browser {browser_id}, error: {response.text}"

@mcp.tool()
def create_browser(
    group_id: str,
    proxy_config: ProxyConfig,
    domain_name: str = None,
    open_urls: List[str] = None,
    cookie: str = None,
    username: str = None,
    password: str = None,
    name: str = None,
    country: str = None,
    sys_app_cate_id: str = None,
    fingerprint_config: Optional[FingerprintConfig] = None,
    storage_strategy: int = None
) -> str:
    """
    Create a new browser profile.
    
    Args:
        group_id (str): The group id of the browser, must be a numeric string (e.g., "123"). You can use get_group_list to get the group list or create a new group, or default is "0"
        proxy_config (ProxyConfig): The proxy configuration of the browser, including:
            - proxy_soft: One of ['brightdata', 'brightauto', 'oxylabsauto', '922S5auto', 'ipideeauto', 'ipfoxyauto', '922S5auth', 'kookauto', 'ssh', 'other', 'no_proxy']
            - proxy_type: One of ['http', 'https', 'socks5', 'no_proxy']
            - proxy_host: The proxy host, e.g., "127.0.0.1"
            - proxy_port: The proxy port, e.g., "8080"
            - proxy_user: The proxy username
            - proxy_password: The proxy password
            - proxy_url: The proxy url, e.g., "http://127.0.0.1:8080"
            - global_config: "0" or "1", default is "0"
        domain_name (str, optional): The domain name of the browser, e.g., facebook.com
        open_urls (List[str], optional): The open urls of the browser, e.g., ["https://www.google.com"]
        cookie (str, optional): The cookie of the browser, e.g., '[{"domain":".baidu.com","expirationDate":"","name":"","path":"/","sameSite":"unspecified","secure":true,"value":"","id":1}]'
        username (str, optional): The username of the browser, e.g., "user"
        password (str, optional): The password of the browser, e.g., "password"
        name (str, optional): The name of the browser, e.g., "My Browser"
        country (str, optional): The country of the browser, e.g., "CN"
        sys_app_cate_id (str, optional): The sys app cate id of the browser, you can use get_application_list to get the application list
        fingerprint_config (FingerprintConfig, optional): The fingerprint configuration of the browser, including:
            - automatic_timezone: "0" or "1", default is "0"
            - timezone: The timezone, e.g., "Asia/Shanghai"
            - language: List of languages, e.g., ["en-US", "zh-CN"]
            - flash: "block" or "allow"
            - fonts: List of fonts, e.g., ["Arial", "Times New Roman"]
            - webrtc: One of ['disabled', 'forward', 'proxy', 'local']
            - browser_kernel_config: Dict with:
                - version: One of ["92", "99", "102", "105", "108", "111", "114", "115", "116", "117", "118", "119", "120", "121", "122", "123", "124", "125", "126", "127", "128", "129", "130", "131", "132", "133", "134", "ua_auto"], default is "ua_auto"
                - type: One of ["chrome", "firefox"], default is "chrome"
            - random_ua: Dict with:
                - ua_version: List of strings for UA versions
                - ua_system_version: List of system versions, can include:
                    - Android versions: ["Android 9", "Android 10", "Android 11", "Android 12", "Android 13"]
                    - iOS versions: ["iOS 14", "iOS 15"]
                    - Windows versions: ["Windows 7", "Windows 8", "Windows 10", "Windows 11"]
                    - Mac versions: ["Mac OS X 10", "Mac OS X 11", "Mac OS X 12", "Mac OS X 13"]
                    - Linux: ["Linux"]
            - tls_switch: "0" or "1"
            - tls: TLS configuration string
        storage_strategy (int, optional): The storage strategy of the browser, default is 0
    """
    request_body = {"group_id": group_id}
    if domain_name:
        request_body["domain_name"] = domain_name
    if open_urls:
        request_body["open_urls"] = open_urls
    if cookie:
        request_body["cookie"] = cookie
    if username:
        request_body["username"] = username
    if password:
        request_body["password"] = password
    if name:
        request_body["name"] = name
    if country:
        request_body["country"] = country
    if sys_app_cate_id:
        request_body["sys_app_cate_id"] = sys_app_cate_id
    if proxy_config:
        request_body["user_proxy_config"] = proxy_config
    if fingerprint_config:
        request_body["fingerprint_config"] = fingerprint_config
    if storage_strategy is not None:
        request_body["storage_strategy"] = storage_strategy

    response = httpx.post(f"{LOCAL_API_BASE}{API_ENDPOINTS['create_browser']}", json=request_body)
    if response.status_code == 200:
        data = response.json()
        if data["code"] == 0:
            formatted_data = '\n'.join(f"{key}: {value}" for key, value in data['data'].items())
            return f"Browser created successfully with:\n{formatted_data}"
        else:
            return f"Failed to create browser, error: {data['msg']}"
    else:
        return f"Failed to create browser, error: {response.text}"

@mcp.tool()
def update_browser(
    browser_id: str,
    proxy_config: Optional[ProxyConfig] = None,
    domain_name: str = None,
    open_urls: List[str] = None,
    cookie: str = None,
    username: str = None,
    password: str = None,
    group_id: str = None,
    name: str = None,
    country: str = None,
    sys_app_cate_id: str = None,
    fingerprint_config: Optional[FingerprintConfig] = None,
    storage_strategy: int = None
) -> str:
    """
    Update an existing browser profile using browser_id.
    
    Args:
        browser_id (str): The user id of the browser to update
        proxy_config (ProxyConfig): The proxy configuration of the browser, including:
            - proxy_soft: One of ['brightdata', 'brightauto', 'oxylabsauto', '922S5auto', 'ipideeauto', 'ipfoxyauto', '922S5auth', 'kookauto', 'ssh', 'other', 'no_proxy']
            - proxy_type: One of ['http', 'https', 'socks5', 'no_proxy']
            - proxy_host: The proxy host, e.g., "127.0.0.1"
            - proxy_port: The proxy port, e.g., "8080"
            - proxy_user: The proxy username
            - proxy_password: The proxy password
            - proxy_url: The proxy url, e.g., "http://127.0.0.1:8080"
            - global_config: "0" or "1", default is "0"
        domain_name (str, optional): The domain name of the browser, e.g., facebook.com
        open_urls (List[str], optional): The open urls of the browser, e.g., ["https://www.google.com"]
        cookie (str, optional): The cookie of the browser, e.g., '[{"domain":".baidu.com","expirationDate":"","name":"","path":"/","sameSite":"unspecified","secure":true,"value":"","id":1}]'
        username (str, optional): The username of the browser, e.g., "user"
        password (str, optional): The password of the browser, e.g., "password"
        group_id (str, optional): The group id of the browser, must be a numeric string (e.g., "123")
        name (str, optional): The name of the browser, e.g., "My Browser"
        country (str, optional): The country of the browser, e.g., "CN"
        sys_app_cate_id (str, optional): The sys app cate id of the browser, you can use get_application_list to get the application list
        fingerprint_config (FingerprintConfig, optional): The fingerprint configuration of the browser, including:
            - automatic_timezone: "0" or "1", default is "0"
            - timezone: The timezone, e.g., "Asia/Shanghai"
            - language: List of languages, e.g., ["en-US", "zh-CN"]
            - flash: "block" or "allow"
            - fonts: List of fonts, e.g., ["Arial", "Times New Roman"]
            - webrtc: One of ['disabled', 'forward', 'proxy', 'local']
            - browser_kernel_config: Dict with:
                - version: One of ["92", "99", "102", "105", "108", "111", "114", "115", "116", "117", "118", "119", "120", "121", "122", "123", "124", "125", "126", "127", "128", "129", "130", "131", "132", "133", "134", "ua_auto"], default is "ua_auto"
                - type: One of ["chrome", "firefox"], default is "chrome"
            - random_ua: Dict with:
                - ua_version: List of strings for UA versions
                - ua_system_version: List of system versions, can include:
                    - Android versions: ["Android 9", "Android 10", "Android 11", "Android 12", "Android 13"]
                    - iOS versions: ["iOS 14", "iOS 15"]
                    - Windows versions: ["Windows 7", "Windows 8", "Windows 10", "Windows 11"]
                    - Mac versions: ["Mac OS X 10", "Mac OS X 11", "Mac OS X 12", "Mac OS X 13"]
                    - Linux: ["Linux"]
            - tls_switch: "0" or "1"
            - tls: TLS configuration string
        storage_strategy (int, optional): The storage strategy of the browser, default is 0
    """
    request_body = {"user_id": browser_id}
    if domain_name:
        request_body["domain_name"] = domain_name
    if open_urls:
        request_body["open_urls"] = open_urls
    if cookie:
        request_body["cookie"] = cookie
    if username:
        request_body["username"] = username
    if password:
        request_body["password"] = password
    if group_id:
        request_body["group_id"] = group_id
    if name:
        request_body["name"] = name
    if country:
        request_body["country"] = country
    if sys_app_cate_id:
        request_body["sys_app_cate_id"] = sys_app_cate_id
    if proxy_config:
        request_body["user_proxy_config"] = proxy_config
    if fingerprint_config:
        request_body["fingerprint_config"] = fingerprint_config
    if storage_strategy is not None:
        request_body["storage_strategy"] = storage_strategy

    response = httpx.post(f"{LOCAL_API_BASE}{API_ENDPOINTS['update_browser']}", json=request_body)
    if response.status_code == 200:
        data = response.json()
        if data["code"] == 0:
            formatted_data = '\n'.join(f"{key}: {value}" for key, value in data['data'].items())
            return f"Browser updated successfully with:\n{formatted_data}"
        else:
            return f"Failed to update browser, error: {data['msg']}"
    else:
        return f"Failed to update browser, error: {response.text}"

@mcp.tool()
def delete_browser(browser_ids: List[str]) -> str:
    """
    Delete one or more browser profiles.
    """
    response = httpx.post(f"{LOCAL_API_BASE}{API_ENDPOINTS['delete_browser']}", json={"user_ids": browser_ids})
    if response.status_code == 200:
        data = response.json()
        if data["code"] == 0:
            return f"Browsers deleted successfully: {', '.join(browser_ids)}"
        else:
            return f"Failed to delete browsers, error: {data['msg']}"
    else:
        return f"Failed to delete browsers, error: {response.text}"

@mcp.tool()
def get_browser_list(group_id: str = None, size: int = None, browser_id: str = None, serial_number: str = None, sort: str = None, order: str = None) -> str:
    """
    Get a list of browser profiles.
    """
    params = {}
    if size:
        params["page_size"] = str(size)
    if browser_id:
        params["user_id"] = browser_id
    if group_id:
        params["group_id"] = group_id
    if serial_number:
        params["serial_number"] = serial_number
    if sort:
        params["user_sort"] = {"[sort]": order or "asc"}

    response = httpx.get(f"{LOCAL_API_BASE}{API_ENDPOINTS['get_browser_list']}", params=params)
    if response.status_code == 200:
        data = response.json()
        if data["code"] == 0:
            return f"Browser list:\n{data['data']['list']}"
        else:
            return f"Failed to get browser list, error: {data['msg']}"
    else:
        return f"Failed to get browser list, error: {response.text}"

@mcp.tool()
def get_opened_browser() -> str:
    """
    Get a list of currently opened browsers.
    """
    response = httpx.get(f"{LOCAL_API_BASE}{API_ENDPOINTS['get_opened_browser']}")
    if response.status_code == 200:
        data = response.json()
        if data["code"] == 0:
            return f"Opened browser list:\n{data['data']['list']}"
        else:
            return f"Failed to get opened browser list, error: {data['msg']}"
    else:
        return f"Failed to get opened browser list, error: {response.text}"

@mcp.tool()
def create_group(group_name: str, remark: str = None) -> str:
    """
    Create a new browser group.
    """
    request_body = {"group_name": group_name}
    if remark:
        request_body["remark"] = remark

    response = httpx.post(f"{LOCAL_API_BASE}{API_ENDPOINTS['create_group']}", json=request_body)
    if response.status_code == 200:
        data = response.json()
        if data["code"] == 0:
            return f"Group created successfully with name: {group_name}{f', remark: {remark}' if remark else ''}"
        else:
            return f"Failed to create group, error: {data['msg']}"
    else:
        return f"Failed to create group, error: {response.text}"

@mcp.tool()
def update_group(group_id: str, group_name: str, remark: str = None) -> str:
    """
    Update an existing browser group.
    """
    request_body = {
        "group_id": group_id,
        "group_name": group_name
    }
    if remark is not None:
        request_body["remark"] = remark

    response = httpx.post(f"{LOCAL_API_BASE}{API_ENDPOINTS['update_group']}", json=request_body)
    if response.status_code == 200:
        data = response.json()
        if data["code"] == 0:
            remark_str = f", remark: {'(cleared)' if remark is None else remark}" if remark is not None else ""
            return f"Group updated successfully with id: {group_id}, name: {group_name}{remark_str}"
        else:
            return f"Failed to update group, error: {data['msg']}"
    else:
        return f"Failed to update group, error: {response.text}"

@mcp.tool()
def get_group_list(name: str = None, size: int = None) -> str:
    """
    Get a list of browser groups.
    """
    params = {}
    if name:
        params["group_name"] = name
    if size:
        params["page_size"] = str(size)

    response = httpx.get(f"{LOCAL_API_BASE}{API_ENDPOINTS['get_group_list']}", params=params)
    if response.status_code == 200:
        data = response.json()
        if data["code"] == 0:
            return f"Group list:\n{data['data']['list']}"
        else:
            return f"Failed to get group list, error: {data['msg']}"
    else:
        return f"Failed to get group list, error: {response.text}"

@mcp.tool()
def get_application_list(size: int = None) -> str:
    """
    Get a list of applications.
    """
    params = {}
    if size:
        params["page_size"] = str(size)

    response = httpx.get(f"{LOCAL_API_BASE}{API_ENDPOINTS['get_application_list']}", params=params)
    if response.status_code == 200:
        data = response.json()
        if data["code"] == 0:
            return f"Application list:\n{data['data']['list']}"
        else:
            return f"Failed to get application list, error: {data['msg']}"
    else:
        return f"Failed to get application list, error: {response.text}"

@mcp.tool()
def move_browser(group_id: str, browser_ids: List[str]) -> str:
    """
    Move browsers to a different group.
    """
    request_body = {
        "group_id": group_id,
        "user_ids": browser_ids
    }

    response = httpx.post(f"{LOCAL_API_BASE}{API_ENDPOINTS['move_browser']}", json=request_body)
    if response.status_code == 200:
        data = response.json()
        if data["code"] == 0:
            return f"Browsers moved successfully to group {group_id}: {', '.join(browser_ids)}"
        else:
            return f"Failed to move browsers, error: {data['msg']}"
    else:
        return f"Failed to move browsers, error: {response.text}"

if __name__ == "__main__":
    # Initialize and run the server
    mcp.run(transport='stdio')
