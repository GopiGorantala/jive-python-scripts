import re
import requests
import json
import csv


class JiveManager:
    def __init__(self):
        self.jiveUsername = ''
        self.jivePassword = ''
        self.jiveInstanceUrl = ''
        self.jiveApiBaseUrl = self.jiveInstanceUrl + '/api/core/v3/'


    def __get(self, url):
        try:
            jive_response = requests.get(url, auth=(self.jiveUsername, self.jivePassword))
            if jive_response.status_code == 500:
                return "Error Response"
            else:
                jive_response = re.sub('\A.*[;]', "", jive_response.text)
                json_response = json.loads(jive_response)
                return json_response
        except Exception as e:
            raise e
        finally:
            pass

    def __post(self, url, params):
        try:
            header = {'content-type': 'application/json'}
            jive_response = requests.post(url, data=params, headers=header, auth=(self.jiveUsername, self.jivePassword))
            jive_response = re.sub('\A.*[;]', "", jive_response.text)
            json_response = json.loads(jive_response)
            return json_response

        except Exception as e:
            raise e
        finally:
            pass

    def __postAs(self, url, params, runAsUserId):
        try:
            header = {'content-type': 'application/json', 'X-Jive-Run-As' : 'userid '+runAsUserId+''}
            jive_response = requests.post(url, data=params, headers=header, auth=(self.jiveUsername, self.jivePassword))
            jive_response = re.sub('\A.*[;]', "", jive_response.text)
            json_response = json.loads(jive_response)
            return json_response

        except Exception as e:
            raise e
        finally:
            pass


    def __put(self, url, params):
        try:
            header = {'content-type': 'application/json'}
            jive_response = requests.put(url, data=params, headers=header, auth=(self.jiveUsername, self.jivePassword))
            jive_response = re.sub('\A.*[;]', "", jive_response.text)
            json_response = json.loads(jive_response)
            return json_response
        except Exception as e:
            raise e
        finally:
            pass

    def __delete(self, url):
        try:
            header = {'content-type': 'application/json'}
            response = requests.delete(url, headers=header, auth=(self.jiveUsername, self.jivePassword))
            return response
        except Exception as e:
            raise e
        finally:
            pass

    def __next_page_url(self, resource_json):
        if 'links' in resource_json:
            if 'next' in resource_json['links']:
                return resource_json['links']['next']
            return None
        return None




    def delete_group_association(self, stream_id, jive_place_id):
        delete_association_url = self.jiveApiBaseUrl + "streams/" + stream_id + "/associations/groups/" + jive_place_id
        self.__delete(delete_association_url)

    def delete_space_association(self, stream_id, jive_place_id):
        delete_association_url = self.jiveApiBaseUrl + "streams/" + stream_id + "/associations/spaces/" + jive_place_id
        self.__delete(delete_association_url)

    def get_group_id(self, groupDisplayName):
        list_of_groups = []
        place_service_url = self.jiveApiBaseUrl+'places/'
        group_url = place_service_url + '?filter=search('+groupDisplayName+')'
        while group_url:
            json_response = self.__get(group_url)
            for group in json_response['list']:
                if group['displayName'] == groupDisplayName:
                    return group['id']
                    break;
            group_url = self.__next_page_url(json_response)

    def get_all_stream_ids_for_user(self, username):
        list_of_streams = []
        people_service_url = self.jiveApiBaseUrl+'people/'
        user_url = people_service_url + 'username/' + username
        json_response = self.__get(user_url)
        streams_url = json_response['resources']['streams']['ref']
        streams_response = self.__get(streams_url)
        for stream in streams_response['list']:
            list_of_streams.append(stream['id'])
        return list_of_streams


    def get_followers_of_place(self, placeId):
        followers = []
        try:
            next_url = self.jiveApiBaseUrl+'places/'+placeId
            resource_json = self.__get(next_url)
            followers_url = resource_json['resources']['followers']['ref']
            next_url = followers_url

            while next_url:
                users = self.__get(next_url)
                for user in users['list']:
                    followers.append(user['displayName'])
                next_url = self.__next_page_url(users)
        except Exception as e:
            print(e)

    def add_expertise(self, personId):
        url = self.jiveApiBaseUrl+'people/'+personId+'/expertise/endorse'
        data = {'[{"name"}]'}
        self.__post(url, data)


    def create_association(self, stream_id, grp_url):
        try:
            uri_array = "[\"" + grp_url + "\"]"
            self.__post(self.jiveApiBaseUrl+"streams/"+stream_id+"/associations", uri_array)
        except Exception as e:
            print(e)
            pass

    def add_member(self, group_member_service_url, user_url):
        post_data = '{"person":"' + user_url + '","state" : "member"}'
        self.__post(group_member_service_url, post_data)

    def force_add_users(self, group_id):
        
        group_place_service_url = self.jiveApiBaseUrl + 'places/' + group_id
        group_member_service_url = self.jiveApiBaseUrl + 'members/places/' + group_id

        with open('users_list.csv', 'rb') as f:
            reader = csv.reader(f)
            for row in reader:
                try:
                    username = row[0]
                    user_data = self.__get(self.jiveApiBaseUrl + 'people/username/' + username)
                    self.add_member(group_member_service_url, user_data)

                    user_streams_url = user_data['resources']['streams']['ref']
                    user_stream_data = self.__get(user_streams_url)
                    for stream in user_stream_data['list']:
                        if stream['name'] == "Email Watches" or stream['source'] == "watches":
                            stream_id = stream['id']
                            self.create_association(stream_id, group_place_service_url)
                except Exception as e:
                    print(e)
                    continue

    def get_group_followers(self, groupId):
        followersIds = []
        next_url = self.jiveApiBaseUrl + "places/" + groupId + "/followers"
        while next_url:
            try:
                resp = self.__get(next_url)
                for usr in resp["list"]:
                    followersIds.append(usr["id"]);
            except Exception as e:
                print(e)
            next_url = self.__next_page_url(resp)
        return followersIds

    def get_group_members(self, groupId):
        memberIds = []
        next_url = self.jiveApiBaseUrl + "members/places/" + groupId
        while next_url:
            try:
                resp = self.__get(next_url)

                for membership in resp["list"]:
                    memberIds.append(membership["person"]["id"])
            except Exception as e:
                print(e)
            next_url = self.__next_page_url(resp)
        return memberIds


    def delete_membership(self, membership_id):
        uri = self.jiveApiBaseUrl + "members/" + membership_id
        requests.delete(uri, auth=(self.jiveUsername, self.jivePassword))

    def check_streams(self):
        next_url = self.jiveApiBaseUrl + "people?count=100&startIndex=0"
        while next_url:
            people_response = self.__get(next_url)
            for person in people_response["list"]:
                try:
                    person_stream_url = person["resources"]["streams"]["ref"]
                    person_stream_data = self.__get(person_stream_url)
                    for stream in person_stream_data["list"]:
                        streamName = ""
                        try:
                            if stream['source'] == "watches":
                                streamName = "Email Watches"
                            elif stream['source'] == "connections":
                                streamName = "Connections"
                            elif stream['source'] == "communications":
                                streamName = "Communications"
                            else:
                                streamName = stream["name"]
                            print("StreamName : "+streamName+", receiveEmail : "+str(stream['receiveEmails']))

                        except Exception as e:
                            print(e)
                            continue
                except Exception as e:
                    print(e)
                    continue
            next_url = self.__next_page_url(people_response)

    def add_stream(self, user_id):
        stream = '{"name":"Email Watches","source":"custom","receiveEmails":"true"}'

        try:
            url = self.jiveApiBaseUrl+"people/" + user_id + "/streams"
            self.__post(url, stream)
        except Exception as e:
            print(e)
            raise e

    def get_all_jive_system_properties(self):
        admin_api_url = self.jiveApiBaseUrl + "admin/properties"
        next_url = admin_api_url

        while next_url:
            response_json = self.__get(next_url)
            for item in response_json["list"]:
                print(item)
            next_url = self.__next_page_url(response_json)

    def create_jive_sys_prop(self):
        properties = [] #properties to add
        for prop in properties:
            system_properties_api_url = self.jiveApiBaseUrl + "admin/properties"
            property_data = '{"name" : "' + prop[0] + '","value" : "' + prop[1] + '","type" : "property"}'
            self.__post(system_properties_api_url, property_data)

    def destroy_jive_system_prop(self):
        props = [] #properties to be destroyed
        for prop in props:
            admin_api_url = self.jiveApiBaseUrl + "admin/properties"
            delete_prop_url = admin_api_url + "/" + prop
            self.__delete(delete_prop_url)

    def get_all_groups(self):
        groupList = []
        next_url = self.jiveApiBaseUrl + "places?filter=type(group)&count=100&startIndex=0"
        while next_url:
            groups_resp = self.__get(next_url)
            for group in groups_resp["list"]:
                groupList.append(group["placeID"] + "," + group["id"] + "," + group["displayName"]);
            next_url = self.__next_page_url(groups_resp)
        return groupList;

    def get_all_private_and_secret_groups(self):
        next_url = self.jiveApiBaseUrl+"places?filter=type(group)"
        while next_url:
            groups_resp = self.__get(next_url)
            for group in groups_resp["list"]:
                if group["groupType"] == "SECRET" or group["type"] == "PRIVATE":
                    print(group["displayName"] + "," + group["name"] + "," + group["groupType"])
            next_url = self.__next_page_url(groups_resp)

    def remove_all_users_from_a_group(self):
        jive_internal_group_id = ""
        jive_group_id = ""

        followerIds = self.get_group_followers(jive_group_id)
        for followerId in followerIds:
            followerData = self.__get(self.jiveApiBaseUrl + 'people/' + followerId)

            user_streams_url = followerData['resources']['streams']['ref']
            user_stream_data = self.__get(user_streams_url)
            for stream in user_stream_data['list']:
                stream_id = stream['id']
                self.delete_group_association(stream_id, jive_internal_group_id)

    def enable_user_accounts(self):
        usernames = [] # array of usernames
        for username in usernames:
            user_url = self.jiveApiBaseUrl + "people/username/" + username
            user_data = self.__get(user_url)


    def get_user_photos(self, username):
        user_url = self.jiveApiBaseUrl + "people/username/"+username
        user_data = self.__get(user_url)
        print(user_data['resources']['avatar']['ref'])
        print(user_data['photos'][0]['value'])
        print(user_data['photos'][1]['value'])

    def create_jive_sys_prop1(self):
        properties = [] #array of properties
        for prop in properties:
            system_properties_api_url = self.jiveApiBaseUrl + "admin/properties"
            property_data = '{"name" : "' + prop[0] + '","value" : "' + prop[1] + '","type" : "property"}'
            print(property_data)
            print(self.__post(system_properties_api_url, property_data))

    def get_all_users(self):
        users = []
        next_url = self.jiveApiBaseUrl + 'people'
        while next_url:
            resp = self.__get(next_url)
            for item in resp['list']:
                users.append(item['jive']['username'])
            next_url = self.__next_page_url(resp)
        return users

    def download_group_content_as_pdf(self, placeID):
        placeContentUrl = self.jiveApiBaseUrl+"places/"+placeID+"/contents"
        contents = self.__get(placeContentUrl);
        for content in contents['list']:
            try:
                content_pdf_link = content['resources']['html']['ref'] + ".pdf"
                file_name = content['subject'] + "_" + content["id"]
                content_json = requests.get(content_pdf_link, auth=(self.jiveUsername, self.jivePassword))
                with open(file_name + ".pdf", "wb") as code:
                    code.write(content_json.content)
            except Exception as e:
                print(e)
                continue

    def get_user_owned_groups(self, username):
        user_url = self.jiveApiBaseUrl + "people/username/" + username
        user = self.__get(user_url)
        user_members_url = user["resources"]["members"]["ref"]
        resp = self.__get(user_members_url)
        for object in resp["list"]:
            if object["state"] == "owner":
                print(object["group"]["displayName"])

    def create_groups(self, groupName, displayName, groupType):
        new_group_data = '{"type":"group","displayName" : "'+displayName+'","name" : "'+groupName+'","groupType" : "'+groupType+'"}'
        jive_places_api_url = self.jiveApiBaseUrl + "places"
        self.__post(jive_places_api_url, new_group_data)


    def get_discussions_from_group(self, groupId):
        placeUrl = self.jiveApiBaseUrl + 'places/' + groupId + '/contents?filter=type(discussion)&count=55&startIndex=0'
        i = 0
        resp = self.__get(placeUrl)
        for item in resp["list"]:
            print(item)

    def send_direct_message(self, userId):
        dmsUrl = self.jiveApiBaseUrl + "dms";
        data = '{ "content": { "text": "aero"},"participants": [ "api/core/v3/people/'+userId+'" ],"subject":"coffee."}'
        self.__post(dmsUrl, data)

    def disable_user(self, userId):
        person_url = self.jiveApiBaseUrl + 'people/' + userId
        personData = self.__get(person_url)
        personData["jive"]["enabled"] = False
        personData = json.dumps(personData)
        self.__put(person_url, personData)

    def get_group_list_with_latest_activity(self):
        for group in self.get_all_groups():
            group_activities = self.__get(self.jiveApiBaseUrl+"places/"+group[0]+"/activities")
            try:
                print(group[2]+","+group_activities["list"][0]["updated"])
            except Exception as e:
                print(group[2]+","+ str(e))
                continue

    def search_group(self, group_url_name):
        group_search_url = self.jiveApiBaseUrl+"places?filter=search("+group_url_name+")";
        while group_search_url:
            groups = self.__get(group_search_url)
            for group in groups["list"]:
                if group["displayName"] == group_url_name:
                    return group
            group_search_url = self.__next_page_url(groups)
    
    def create_content_in_place(self, placeId):
        url = self.jiveApiBaseUrl+"places/"+placeId+"/contents"
        dat = '{"content":{"type": "text/html","text": "<body><p>Some interesting content</p></body>"},"subject": "New Document","type": "document"}'
        self.__post(url, dat)

    def update_group(self, group_id):
        group_uri = self.jiveApiBaseUrl+"places/"+group_id
        group = self.__get(group_uri)
        group["groupType"] = "SECRET"
        self.__put(group_uri, json.dumps(group))




