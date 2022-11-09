#! /usr/bin/env python3

import json
from functools import cached_property
from os import chdir
from pathlib import Path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import Resource, build

HOME_DIR = Path.home()
WORKING_DIR = HOME_DIR / ".md2docs"


class GoogleDocs:
    def __init__(
        self, credentials_json_file: str, token_json_file: str, scopes: list[str]
    ):
        self.credentials_json_file = credentials_json_file
        self.token_json_file = token_json_file
        self.scopes = scopes
        self.creds: Credentials = None
        self.authenticated = False

    def load_credentials_from_token_file(self):
        self.creds = Credentials.from_authorized_user_file(
            self.token_json_file, self.scopes
        )

    def trigger_authentication_flow(self):
        flow = InstalledAppFlow.from_client_secrets_file(
            self.credentials_json_file, self.scopes
        )
        self.creds = flow.run_local_server(port=0)

    def authenticate(self):
        # TOKEN_FILE stores the user's access and refresh tokens, and is created
        # automatically when the authorization flow completes for the first time.
        new_token = False

        if Path(self.token_json_file).exists():
            self.load_credentials_from_token_file()
            if self.creds.expired and self.creds.refresh_token:
                self.creds.refresh(Request())
                new_token = True

        # If there are no (valid) credentials available, let the user log in.
        if not self.creds or not self.creds.valid:
            self.trigger_authentication_flow()
            new_token = True

        # Save the credentials for the next run
        if new_token:
            Path(self.token_json_file).write_text(self.creds.to_json())

        print(
            f"Credentials used: {self.credentials_json_file}\nToken used: {self.token_json_file}"
        )
        self.authenticated = True

    @cached_property
    def service(self) -> Resource:
        return build("docs", "v1", credentials=self.creds)

    def sync_document(self, file_path: str, document_id: str):
        # ref: https://developers.google.com/docs/api/reference/rest/v1/documents/create
        # add support for minimal markdown support
        #  parse markdown to gdocs format
        #  use batchUpdate to update the document
        # this will give more control over document updates + formatting
        # TODO: better document update than del + insert by ^^^
        document = self.service.documents().get(documentId=document_id).execute()
        endIndex = max([x["endIndex"] for x in document["body"]["content"]])
        change_requests = []

        if endIndex > 2:
            change_requests.append(
                {
                    "deleteContentRange": {
                        "range": {"startIndex": 1, "endIndex": endIndex - 1}
                    }
                }
            )

        change_requests.append(
            {
                "insertText": {
                    "text": Path(file_path).read_text(),
                    "location": {
                        "index": 1,
                    },
                }
            }
        )

        self.service.documents().batchUpdate(
            documentId=document_id,
            body={"requests": change_requests},
        ).execute()


def main():
    WORKING_DIR.mkdir(exist_ok=True)
    chdir(WORKING_DIR)

    # If modifying these scopes, delete the token file.
    SCOPES = ["https://www.googleapis.com/auth/documents"]
    CREDENTIALS_JSON_FILE = WORKING_DIR / "credentials.json"
    TOKEN_FILE = WORKING_DIR / "tokens.json"
    MD2DOCS_SETTINGS_FILE = WORKING_DIR / "settings.json"

    if not MD2DOCS_SETTINGS_FILE.exists():
        raise FileNotFoundError(
            f"Settings file not found. Please create {MD2DOCS_SETTINGS_FILE}"
        )

    md2docs_settings = json.loads(MD2DOCS_SETTINGS_FILE.read_text())

    gd = GoogleDocs(
        credentials_json_file=CREDENTIALS_JSON_FILE,
        token_json_file=TOKEN_FILE,
        scopes=SCOPES,
    )

    for document in md2docs_settings:
        source = document["source"]
        target = document["target"]
        last_synced = document.get("last_synced")
        last_modified = Path(source).stat().st_mtime

        if (not last_synced) or (last_modified > last_synced):
            if not gd.authenticated:
                gd.authenticate()
            print(f"Syncing {source} to {target}")
            gd.sync_document(source, target)
            document["last_synced"] = last_modified

    MD2DOCS_SETTINGS_FILE.write_text(json.dumps(md2docs_settings, indent=4))


if __name__ == "__main__":
    main()
