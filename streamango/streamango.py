import os
import requests

from .exceptions import (BadRequestException, BandwidthUsageExceeded,
                         FileNotFoundException, PermissionDeniedException,
                         ServerErrorException,
                         UnavailableForLegalReasonsException)


class Streamango(object):
    api_url = 'https://api.fruithosted.net'

    def __init__(self,
                 login: str=os.environ.get('STREAMANGO_LOGIN'),
                 key: str=os.environ.get('STREAMANGO_KEY')):
        """
        Initializes Streamango instance from environment variables:
        STREAMANGO_LOGIN for login and STREAMANGO_KEY for key.
        You can also pass login and key directly.

        :param str api_login: API login for streamango.com.
        :param str api_key: API key for streamango.com.
        :rtype: None
        """
        self.login = login
        self.key = key

    @classmethod
    def _check_status(cls, response_json: dict):
        """
        Check status of response,
        raise exception if status is not 200.

        :param dict response_json: Api response as dict.
        :rtype: None
        :raises:
            :class:`streamango.exceptions.BadRequestException`
            :class:`streamango.exceptions.PermissionDeniedException`
            :class:`streamango.exceptions.FileNotFoundException`
            :class:`streamango.exceptions.UnavailableForLegalReasonsException`
            :class:`streamango.exceptions.BandwidthUsageExceeded`
            :class:`streamango.exceptions.ServerErrorException`
        """
        status = response_json['status']
        msg = response_json['msg']

        if status == 400:
            raise BadRequestException(msg)
        elif status == 403:
            raise PermissionDeniedException(msg)
        elif status == 404:
            raise FileNotFoundException(msg)
        elif status == 451:
            raise UnavailableForLegalReasonsException(msg)
        elif status == 509:
            raise BandwidthUsageExceeded(msg)
        elif status >= 500:
            raise ServerErrorException(msg)

    @classmethod
    def _process_response(cls, response_json: dict) -> dict:
        """
        Check response status for errors, return response results.

        :param dict response_json: Api response as dict.
        :rtype: dict
        """
        cls._check_status(response_json)
        return response_json['result']

    def _get(self, path: str, params: dict={}) -> dict:
        """
        Make GET request with given parameters, return response
        processed by :func:`streamango.Streamango._process_response`.

        :param str path: Relative path to api method.
        :param dict params: Parameters to be sent in the GET request.
        :rtype: dict
        """
        params.update({'login': self.login, 'key': self.key})
        response_json = requests.get(f'{self.api_url}/{path}', params).json()
        return self._process_response(response_json)

    def account_info(self) -> dict:
        """
        Request account related information e.g. rewards, ID etc.

        :rtype: dict
        :returns: Dict with account related information.

        .. code-block:: json

            {
                "extid": "extuserid",
                "email": "jeff@streamango.com",
                "signup_at": "2015-01-09 23:59:54",
                "storage_left": -1,
                "storage_used": "32922117680",
                "traffic": {
                  "left": -1,
                  "used_24h": 0
                },
                "balance": 0
            }

        """
        return self._get('account/info')

    def prepare_download(self, file_id: str) -> dict:
        """
        Request download ticket.

        :param str file_id: Id of file to be downloaded.
        :rtype: dict
        :returns: Dict with ticket info.

        .. code-block:: json

            {
              "ticket": "72fA-_Lq8Ak~~1440353112~n~~0~nXtN3RI-nsEa28Iq",
              "captcha_url": "https://streamango.com/dlcaptcha/b92eY_nfj.png",
              "captcha_w": 140,
              "captcha_h": 70,
              "wait_time": 10,
              "valid_until": "2015-08-23 18:20:13"
            }

        """
        return self._get('file/dlticket', params={'file': file_id})

    def get_download_link(self, file_id: str, ticket: str,
                          captcha_response: str='') -> dict:
        """
        Requests direct download link for a file with ticket.

        :param str file_id: Id of file to be downloaded.
        :param str ticket: Ticket id from
            :func:`streamango.Streamango.prepare_download`.
        :param str captcha_response: Sometimes
            :func:`streamango.Streamango.prepare_download` will have url
            with captcha to solve. Pass solution here.
        :rtype: dict
        :returns: Dict with file download info.

        .. code-block:: json

            {
              "name": "asdf.txt",
              "size": 12345,
              "sha1": "2fd4e1c67a2d28fced849ee1bb76e7391b93eb12",
              "content_type": "plain/text",
              "upload_at": "2011-01-26 13:33:37",
              "url": "https://abvzps.example.com/dl/l/4spxX_-cSO4/asdf.txt",
              "token": "4spxX_-cSO4"
            }

        """
        params = {'ticket': ticket, 'file': file_id}

        if captcha_response:
            params['captcha_response'] = captcha_response

        return self._get('file/dl', params)

    def file_info(self, file_id: str) -> dict:
        """
        Request info for a specific file.

        :param str file_id: File-ID(s), single file or
            comma-separated (max. 50)
        :rtype: dict
        :returns: Dict with file info

        .. code-block:: json

            {
               "72fA-_Lq8Ak3": {
                    "id": "72fA-_Lq8Ak3",
                    "status": 200,
                    "name": "The quick brown fox.txt",
                    "size": 123456789012,
                    "sha1": "2fd4e1c67a2d28fced849ee1bb76e7391b93eb12",
                    "content_type": "plain/text",
                },
                "72fA-_Lq8Ak4": {
                    "id": "72fA-_Lq8Ak4",
                    "status": 500,
                    "name": "The quick brown fox.txt",
                    "size": false,
                    "sha1": "2fd4e1c67a2d28fced849ee1bb76e7391b93eb12",
                    "content_type": "plain/text",
                }
            }

        """
        return self._get('file/info', params={'file': file_id})

    def upload_link(self, folder_id: str='', sha1: str='',
                    httponly: bool=False) -> dict:
        """
        Request upload url. Note: If folder_id is not provided,
        it will make and upload link to the ``Home`` folder.

        :param str folder_id: Folder-ID to upload to.
        :param sha1 str: Expected sha1. If sha1 of uploaded file
            doesn't match this value, upload fails.
        :param bool httponly: If this is set to true,
            use only http upload links.
        :rtype: dict
        :returns: Dict with upload info.

        .. code-block:: json

            {
                "url": "https://13abc37.example.com/ul/fCgaPthr_ys",
                "valid_until": "2015-01-09 00:02:50"
            }

        """
        kwargs = {'folder': folder_id, 'sha1': sha1, 'httponly': httponly}
        params = {key: value for key, value in kwargs.items() if value}
        return self._get('file/ul', params=params)

    def upload_file(self, file_path: str, folder_id: str='',
                    sha1: str='', httponly: bool=False) -> dict:
        """
        Request upload url with :func:`streamango.Streamango.upload_link`.
        Upload given file. Return dict with file info. Note: If folder_id
        is not provided, the file will be uploaded to ``Home`` folder.

        :param str file_path: Path to file to be uploaded.
        :param str folder_id: Folder-ID to upload to.
        :param sha1 str: Expected sha1. If sha1 of uploaded file
            doesn't match this value, upload fails.
        :param bool httponly: If this is set to true,
            use only http upload links.
        :rtype: dict
        :returns: Dict with upload info.

        .. code-block:: json

            {
                "content_type": "application/zip",
                "id": "0yiQTPzi4Y4",
                "name": 'favicons.zip',
                "sha1": 'f2cb05663563ec1b7e75dbcd5b96d523cb78d80c',
                "size": '24160',
                "url": 'https://streamango.com/f/0yiQTPzi4Y4/favicons.zip'
            }

        """
        upload_url_response_json = self.upload_link(
            folder_id=folder_id, sha1=sha1, httponly=httponly)
        upload_url = upload_url_response_json['url']

        with open(file_path, 'rb') as f:
            response_json = requests.post(
                upload_url,
                files={'upload_file': f}
            ).json()

        self._check_status(response_json)
        return response_json['result']

    def remote_upload(self, remote_url: str, folder_id: str='',
                      headers: dict={}) -> dict:
        """
        Add file to Remote Upload. Note: If folder_id is not provided,
        the file will be uploaded to ``Home`` folder.

        :param str remote_url: Direct link to file.
        :param str folder_id: Folder-ID to upload to.
        :param dict headers: additional HTTP headers
            (e.g. Cookies or HTTP Basic-Auth)
        :rtype: dict
        :returns: Dict with remote upload info.

        .. code-block:: json

            {
                "id": "12",
                "folderid": "4248"
            }

        """
        kwargs = {'folder': folder_id, 'headers': headers}
        params = {'url': remote_url}
        params.update({key: value for key, value in kwargs.items() if value})

        return self._get('remotedl/add', params=params)

    def remote_upload_status(self, limit: int=5, remote_upload_id: str=''):
        """
        Request remote file upload status.
        Return dict with remote uploads info.

        :param int limit: Maximum number of results
            (Default: 5, Maximum: 100).
        :param str remote_upload_id: Remote Upload ID.
        :rtype: dict
        :returns: Dict with remote upload status.

        .. code-block:: json

            {
                "24": {
                  "id": "24",
                  "remoteurl": "http://proof.ovh.net/files/100Mio.dat",
                  "status": "new",
                  "folderid": "4248",
                  "added": "2015-02-21 09:20:26",
                  "last_update": "2015-02-21 09:20:26",
                  "extid": False,
                  "url": False
                },
                "22": {
                  "id": "22",
                  "remoteurl": "http://proof.ovh.net/files/1Gio.dat",
                  "status": "downloading",
                  "bytes_loaded": "823997062",
                  "bytes_total": "1073741824",
                  "folderid": "4248",
                  "added": "2015-02-21 09:20:26",
                  "last_update": "2015-02-21 09:21:56",
                  "extid": False,
                  "url": False
                }
            }

        """

        kwargs = {'limit': limit, 'id': remote_upload_id}
        params = {key: value for key, value in kwargs.items() if value}

        return self._get('remotedl/status', params=params)

    def list_folder(self, folder_id: str='') -> dict:
        """
        Request list of files and folders in specified folder. Note:
        If folder_id is not provided, ``Home`` folder will be listed.

        :param str folder_id: Id of folder to be listed.
        :rtype: dict
        :returns: Dict with folders info.

        .. code-block:: json

            {
              "folders": [
                {
                  "id": "5144",
                  "name": ".videothumb"
                },
                {
                  "id": "5792",
                  "name": ".subtitles"
                }
              ],
              "files": [
                {
                  "name": "asd.mp4",
                  "sha1": "c6531f5ce9669d6547023d92aea4805b7c45d133",
                  "folderid": "4258",
                  "upload_at": "1419791256",
                  "status": "active",
                  "size": "5114011",
                  "content_type": "video/mp4",
                  "download_count": "48",
                  "cstatus": "ok",
                  "link": "https://streamango.com/f/UPPjeAk--30/asd.mp4",
                  "linkextid": "UPPjeAk--30"
                }
              ]
            }

        """
        params = {'folder': folder_id} if folder_id else {}

        return self._get('file/listfolder', params=params)

    def rename_folder(self, folder_id: str, name: str) -> bool:
        """
        Rename a folder. Note: folder_id(s) can be obtained through
        :func:`streamango.Streamango.list_folder` method.

        :param str folder_id: Id of folder to be renamed.
        :param str name: New name for given folder.
        :rtype: bool
        :returns: True if folder is renamed, otherwise False.
        """
        params = {'folder': folder_id, 'name': name}
        return self._get('file/renamefolder', params=params)

    def rename_file(self, file_id: str, name: str) -> bool:
        """
        Rename a file.

        :param str file_id: Id of the file to be renamed.
        :param str name: New name for given folder.
        :rtype: bool
        :returns: True if file is renamed, otherwise False.
        """
        params = {'file': file_id, 'name': name}
        return self._get('file/rename', params=params)

    def delete_file(self, file_id: str) -> bool:
        """
        Delete a file.

        :param str file_id: Id of the file to be deleted.
        :rtype: bool
        :returns: True if file is deleted, otherwise False.
        """
        return self._get('file/delete', params={'file': file_id})

    def convert_file(self, file_id: str) -> bool:
        """
        Convert your uploaded files into a browser stream friendly
        version (h.264 o. mp4).

        :param str file_id: Id of the file to be converted.
        :rtype: bool
        :returns: True if conversion started, otherwise False.
        """
        return self._get('file/convert', params={'file': file_id})

    def running_conversions(self, folder_id: str='') -> list:
        """
        Get running file converts by folder. Note: If folder_id is
        not provided, ``Home`` folder will be used.

        :param str folder_id: Id of the folder to get
            running conversions from.
        :rtype: list
        :returns: List of dicts, each dict
            represents a file conversion info.

        .. code-block:: json

                [
                  {
                    "name": "Geysir.AVI",
                    "id": "3565411",
                    "status": "pending",
                    "last_update": "2015-08-23 19:41:40",
                    "progress": 0.32,
                    "retries": "0",
                    "link": "https://streamango.com/f/f02JFG293J8/Geysir.AVI",
                    "linkextid": "f02JFG293J8"
                  }
                ]

        """
        params = {'folder': folder_id} if folder_id else {}
        return self._get('file/runningconverts', params=params)

    def failed_conversions(self) -> NotImplementedError:
        """
        Not yet implemented, streamango.com says "Not ready yet".

        :raises: :class:`NotImplementedError`
        """
        raise NotImplementedError

    def splash_image(self, file_id: str) -> str:
        """
        Request videos splash image (thumbnail).

        :param str file_id: Id of the target file.
        :rtype: str
        :returns: Url for the splash image.
        """
        return self._get('file/getsplash', params={'file': file_id})
