from collections import defaultdict
import datetime
import json
import logging

import requests

from django.conf import settings
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse


logger = logging.getLogger(__name__)


API_URLS = {
    "get_time_zone": "/api/getTimeZoneList",
    "get_sche_info_avl_time_list": "/api/getScheduleInfoAvailableTimesList",
    "add_adhoc_process": "/api/addAdHocProcess",
    "remove_reservation": "/api/removeReservation",
    "client_activity_report": "/api/clientActivityReport",
    "student_reservation_list": "/api/getStudentReservationList",
    "begin_reservation": "/api/beginReservation",
    "edit_student": "/api/editStudent",
}

BASE_URL = "https://"+settings.PROCTORU_API
HEADER = {"Authorization-Token": settings.PROCTORU_TOKEN}

def query_api(request_method, url, data):
    data["time_sent"] = datetime.datetime.utcnow().isoformat()

    try:
        student_activity = request_method(
                url,
                data=data,
                headers=HEADER
            ).content
    except requests.ConnectionError as e:
            logger.exception(e)
            return {"error": "Connection error while connecting to {}".format(url)}

    student_activity_json = json.loads(student_activity)
    if student_activity_json["response_code"] != 1:
        if student_activity_json["message"] == "stale request" :
            logger.error("Error in ProctorU API configuration, received : stale request")
            return {"error":student_activity_json["message"]}
        else:
            logger.error("ProctorU API error, message : {}".format(student_activity_json["message"]) )
            return {"error":student_activity_json["message"]}

    return student_activity_json


def is_in_prod():
    """
    Utility function to tell in we are in test, dev ou prepro / prod settings.
    We don't query the users the same way according the setup.

    :return: boolean are we in preprod / prod or not
    """
    """
    :return:
    """
    try:
        settings.TEST_ROOT  # are we in test mode ?
    except AttributeError:
        test = False
    else:
        test = True

    if test:
        return False  # if we are in test, we are not in prod

    return (not settings.DEBUG)  # if we are in debug mode, we are not in prod


def extract_infos(report):
    tmp = {
        "Student": report["Student"],
        "ProctorNotes": report["ProctorNotes"],
        "UniqueId": report["UniqueId"],
        "ReservationNo": report["ReservationNo"],
        "CheckID": report["CheckID"],
        "StartDate": report["StartDate"],
        "Authenticated": report["Authenticated"],
        "IncidentReport": report["IncidentReport"],
        "Escalated": report["Escalated"],
        "fun_user_url": None,
    }
    return tmp

def get_protectU_students(course_name, course_run):
    data = request_infos()

    student_activity = query_api(requests.post,
                                 BASE_URL + API_URLS["client_activity_report"],
                                 data)
    if "error" in student_activity:
        return student_activity

    filtered_reports = filter_reports_for_course(course_name, course_run, data, student_activity)
    if "error" in filtered_reports:
        return filtered_reports

    return aggregate_reports_per_user(filtered_reports)


def aggregate_reports_per_user(filtered_reports):
    """
    Aggregate the lines present in the API according the user.
    The API returns a line for each events, but we are really interested in the "profile" for each user.

    ProctorU API seems bugged, it contains duplicated lines (usually consecutive), so we also remove the consecutive
    duplicates.

    :param filtered_reports: iterable with the ProctorU reports filtered with the course of interest
    :return: dict with the procterU user ID as key and the list of "actions" / reports for this user
    """
    filtered_reports.sort(key=lambda d: d["Student"])

    id_ = filtered_reports[0]["UniqueId"]
    identifiers = [id_]
    event_users = defaultdict(list)
    event_users[id_].append(extract_infos(filtered_reports[0]))

    prec_json = filtered_reports[0]
    for report in filtered_reports[1:]:
        tmp = extract_infos(report)
        if report != prec_json:
            event_users[report["UniqueId"]].append(tmp)
            identifiers.append(report["UniqueId"])
        prec_json = report

    if not is_in_prod():
        fun_users = User.objects.filter(last_name__in=identifiers)
    else:
        fun_users = User.objects.filter(id__in=identifiers)

    for user in fun_users:
        if not is_in_prod():
            id_ = user.last_name
        else:
            id_ = user.id

        url = reverse("backoffice:user-detail", args=[user.username])
        event_users[id_][0]["fun_user_url"] = url
    return dict(event_users)


def filter_reports_for_course(course_name, course_run, api_query, student_activity):
    """
    Only keep the course of interest from the API query.
    This should be done API side, but it is not possible for the moment :(

    :param course_name: str course ID
    :param course_run: str session ID
    :param api_query: dict with the API request (contains the dates for the logs)
    :param student_activity: dict with the API response
    :return: dict with the API response about the course
    """
    exam_id = "{} {}".format(course_name, course_run)
    reports = student_activity["data"]
    if not reports:
        mess = "Empty response from the API"
        logger.info(mess)
        return {"error": mess}
    filtered_reports = [report for report in reports if exam_id in report["Test"]]
    if not filtered_reports:
        mess = "No student for course {} between {} and {}".format(exam_id,
                                                                   api_query["start_date"],
                                                                   api_query["end_date"])
        logger.info(mess)
        return {"error": mess}
    return filtered_reports


def request_infos():
    start = datetime.datetime.today() - datetime.timedelta(days=100)
    end = datetime.datetime.today() + datetime.timedelta(days=100)
    start_date = start.isoformat()
    end_date = end.isoformat()
    data = {
        "end_date": end_date,
        "start_date": start_date,
    }
    return data
