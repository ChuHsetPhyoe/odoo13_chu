from odoo import http, fields, tools, _
from odoo.http import request, route
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT
import geopy.distance
from operator import itemgetter

import random
import string
from random import randint
import urllib
import json
from passlib.context import CryptContext
from datetime import datetime, timedelta
import base64
import os
# import jwt
import logging
import json
from odoo import fields, http
from odoo.http import request

_logger = logging.getLogger(__name__)


class SaleMobileAppController(http.Controller):

    @http.route('/CheckUserLogin', type='json', auth='public', cors='*')
    def check_user_login(self, **kwargs):
        """ Function to check the login credentials, return SUCCESS or FAILURE """
        status = message = token_num = user_name = ''
        company_id = response_code = 0
        if kwargs:
            _logger.info("Arguments: %s", kwargs)
            if not kwargs.get('login', ''):
                return {'status': 'FAILED', 'message': 'No username supplied!'}
            if not kwargs.get('password', ''):
                return {'status': 'FAILED', 'message': 'No password supplied!'}
            try:
                uid = request.session.authenticate(request.db, kwargs.get('login', ''), kwargs.get('password', ''))
                if not uid:
                    status = 'FAILED'
                    message = 'Invalid Login Id or Password!'
                    response_code = 1007
                else:
                    status = 'SUCCESS'
                    message = 'Login Successful!'
                    user = request.env['res.users'].sudo().browse(uid)
                    company_id = user.sudo().company_id.id
                    user_name = user.name
                    token = ''.join(
                        random.SystemRandom().choice(string.ascii_uppercase + string.digits) for _ in range(15))
                    user.token = token
                    token_num = token
            except Exception as e:
                _logger.info("Invalid Login Id or Password!")
                status = 'FAILED'
                message = 'Invalid Login Id or Password ' + str(e.args)
        else:
            status = 'FAILED'
            message = 'No params supplied, Please contact administrator!'
        return {'status': status, 'message': message, 'token': token_num, 'response_code': response_code,
                'company_id': company_id, 'user_name': user_name}

    @http.route('/GetAssignmentsDetails', type='json', auth='public', cors='*')
    def get_assignment(self, **kwargs):
        ''' function will return all assignment related to user '''
        assignment_obj = request.env['fleet.assigned.task']
        # hr_employee = request.env['hr.employee']
        status, message, assignment_list = '', '', []
        response_code = 0
        if kwargs:
            _logger.info("Arguments: %s", kwargs)
            if not kwargs.get('token', ''):
                return {'status': 'FAILED', 'message': 'No token supplied!'}
            try:
                token = kwargs.get('token', '')
                user = request.env['res.users'].sudo().search([('token', '=', token)])
                if not user:
                    status = 'FAILED'
                    message = 'Login Failed! '
                    response_code = 1007
                else:
                    #employee = hr_employee.sudo(user.id).search([('user_id', '=', user.id)], limit=1)
                    # employee = hr_employee.sudo().search([('address_home_id','=',user.partner_id.id)], limit=1)
                    _logger.info("Employee ID: %s", user)
                    #assignment = assignment_obj.sudo(user.id).search([
                    #    ('employee_id', '=', employee.id), ('state', '=', 'progress')])
                    assignment = assignment_obj.sudo().search([
                        ('user_id', '=', user.id), ('state', '=', 'progress')])
                    _logger.info("Assignment ID: %s", assignment)
                    if assignment:
                        # for assignments in assignment:
                        #     assignment_dict = {
                        #         'assignment_id': assignments.id,
                        #         'route_id': assignments.routeId.id,
                        #         'route': assignments.routeId.name,
                        #         'Date': assignments.date,
                        #     }
                        #     assignment_list.append(assignment_dict)
                        for assignments in assignment:
                            assignment_dict = {
                                'assignment_id': assignments.id,
                                'route_id': assignments.routeId.id,
                                'route': assignments.name,
                                'Date': assignments.date,
                            }
                            assignment_list.append(assignment_dict)
                        status = 'SUCCESS'
                        message = 'User Assignment Details'
                    else:
                        status = 'FAILED'
                        message = 'No User Assignment Found!'
            except Exception as e:
                _logger.info("Error: %s", e.args)
                status = 'FAILED'
                message = 'Error: ' + str(e.args)
        else:
            status = 'FAILED'
            message = 'No params supplied, Please contact administrator!'
        return {'status': status, 'message': message, 'assignment_list': assignment_list,
                'response_code': response_code}

    @http.route('/GetPartnersfromRoute', type='json', auth='public', cors='*')
    def get_route_partners(self, **kwargs):
        ''' function will return all partners related to the selected assignment by user '''
        assignment_obj = request.env['fleet.assigned.task']
        # hr_employee = request.env['hr.employee']
        assignment_task_obj = request.env['fleet.assignment.item']
        status, message, partner_list = '', '', []
        response_code = 0
        if kwargs:
            _logger.info("Arguments: %s", kwargs)
            if not kwargs.get('token', ''):
                return {'status': 'FAILED', 'message': 'No token supplied!'}
            if not kwargs.get('assignment_id', ''):
                return {'status': 'FAILED', 'message': 'Assignment Details has not been supplied!'}
            if not kwargs.get('route_id', ''):
                return {'status': 'FAILED', 'message': 'Route Details has not been supplied!'}
            try:
                token = kwargs.get('token', '')
                assignment_id = kwargs.get('assignment_id', '')
                salesperson_lat = kwargs.get('salesperson_lat', '')
                salesperson_long = kwargs.get('salesperson_long', '')
                user = request.env['res.users'].sudo().search([('token', '=', token)])
                assignment = assignment_obj.sudo().search([('id', '=', assignment_id)])
                if not user:
                    status = 'FAILED'
                    message = 'Login Failed! '
                    response_code = 1007
                elif not assignment:
                    status = 'FAILED'
                    message = 'Assignment not found!'
                    response_code = 1007
                elif not assignment.routeId:
                    status = 'FAILED'
                    message = 'Route not found!'
                    response_code = 1007
                elif not salesperson_lat:
                    status = 'FAILED'
                    message = 'Latitude not supplied!'
                    response_code = 1007
                elif not salesperson_long:
                    status = 'FAILED'
                    message = 'Longitude not supplied!'
                    response_code = 1007
                else:
                    if assignment:
                        # for partners in assignment.routeId.partner_ids:
                        for partners in assignment.partner_ids:
                            coords_1 = (salesperson_lat, salesperson_long)
                            coords_2 = (partners.partner_latitude, partners.partner_longitude)
                            distance = geopy.distance.geodesic(coords_1, coords_2).km
                            task_ids = assignment_task_obj.sudo().search([
                                ('assigned_task_id', '=', assignment.id),
                                ('partner_id', '=', partners.id)
                            ])
                            partner_dict = {
                                'partner_id': partners.id,
                                'partner_name': partners.name,
                                'address_line1': partners.street or '',
                                'address_line2': partners.street2 or '',
                                'town': partners.town.name or '',
                                'city': partners.city.name or '',
                                'state': partners.state_id.name or '',
                                'zip': partners.zip or '',
                                'country': partners.country_id.name or '',
                                'phone': partners.phone or '',
                                'mobile': partners.mobile or '',
                                'email': partners.email or '',
                                'website': partners.website or '',
                                'latitude': partners.partner_latitude,
                                'longitude': partners.partner_longitude,
                                'route_id': assignment.routeId.id,
                                'distance_from_current_location_km': distance
                            }
                            # *** Commented out by Yoma ***
                            if task_ids:
                               if all(task.status == 'completed' for task in task_ids):
                                   partner_dict['partner_task'] = 1
                               else:
                                   partner_dict['partner_task'] = 0
                            else:
                               partner_dict['partner_task'] = 0
                            partner_list.append(partner_dict)
                            partner_list = sorted(partner_list, key=itemgetter('distance_from_current_location_km'))
                        status = 'SUCCESS'
                        message = 'Partner Details based on Assignment & Route'
                    else:
                        status = 'FAILED'
                        message = 'Partners not Found!'
            except Exception as e:
                _logger.info("Error: %s", e.args)
                status = 'FAILED'
                message = 'Error: ' + str(e.args)
        else:
            status = 'FAILED'
            message = 'No params supplied, Please contact administrator !'
        ResConfig = request.env['res.config.settings']
        default_values = ResConfig.sudo().default_get(list(ResConfig.fields_get()))
        if 'maximum_distance_allowed' in default_values:
            maximum_distance_allowed = default_values.get('maximum_distance_allowed')
        else:
            maximum_distance_allowed = 0.0
        return {'status': status, 'message': message, 'geo_fence': maximum_distance_allowed, 'partner_list': partner_list,
                'response_code': response_code}

    @http.route('/ConfirmPartnerCheckIn', type='json', auth='public', cors='*')
    def confirm_partner_checkin(self, **kwargs):
        ''' function will return all partners related to the selected assignment by use '''
        assignment_obj = request.env['fleet.assigned.task']
        hr_employee = request.env['hr.employee']
        partner_obj = request.env['res.partner']
        partner_visit_obj = request.env['partner.visit']
        status, message, partner_list = '', '', []
        response_code = 0
        if kwargs:
            _logger.info("Arguments: %s", kwargs)
            if not kwargs.get('token', ''):
                return {'status': 'FAILED', 'message': 'No token supplied!'}
            if not kwargs.get('assignment_id', ''):
                return {'status': 'FAILED', 'message': 'Assignment Details has not been supplied!'}
            if not kwargs.get('route_id', ''):
                return {'status': 'FAILED', 'message': 'Route Details has not been supplied!'}
            try:
                token = kwargs.get('token', '')
                assignment_id = kwargs.get('assignment_id', '')
                checkin_time = kwargs.get('check_in_datetime', '')
                checkin_lat = kwargs.get('check_in_latitude', '')
                checkin_long = kwargs.get('check_in_longitude', '')
                partner_ = kwargs.get('partner_id', '')
                user = request.env['res.users'].sudo().search([('token', '=', token)])
                assignment = assignment_obj.sudo().search([('id', '=', assignment_id)])
                partner = partner_obj.sudo().search([('id', '=', partner_)])
                if not user:
                    status = 'FAILED'
                    message = 'Login Failed! '
                    response_code = 1007
                elif not assignment:
                    status = 'FAILED'
                    message = 'Assignment not found!'
                    response_code = 1007
                elif not assignment.routeId:
                    status = 'FAILED'
                    message = 'Route not found!'
                    response_code = 1007
                elif not partner:
                    status = 'FAILED'
                    message = 'Partner not found!'
                    response_code = 1007
                else:
                    # employee = hr_employee.sudo().search([('user_id', '=', user.id)], limit=1)
                    # employee = hr_employee.sudo().search([('address_home_id','=',user.partner_id.id)], limit=1)
                    _logger.info("Employee ID: %s", user)
                    # assignment_id = assignment_obj.sudo(user.id).search([('id', '=', assignment.id)])
                    assignment_id = assignment_obj.sudo().search([('id', '=', assignment.id)])
                    _logger.info("Assignment ID: %s", assignment_id)
                    if assignment:
                        # for partners in assignment.routeId.partner_ids:
                        partner_dict = {
                            'partner_id': partner.id,
                            'cin_datetime': datetime.now(),
                            'cin_lat': checkin_lat,
                            'cin_long': checkin_long,
                            'assignment_id': assignment.id,
                            'user_id': user.id
                        }
                        partner_visit_obj.sudo().create(partner_dict)
                        status = 'SUCCESS'
                        message = 'Check-in Successful!'
                    else:
                        status = 'FAILED'
                        message = 'Check-in Failed'
            except Exception as e:
                _logger.info("Error: %s", e.args)
                status = 'FAILED'
                message = 'Error: ' + str(e.args)
        else:
            status = 'FAILED'
            message = 'No params supplied, Please contact administrator !'
        return {'status': status, 'message': message, 'partner_list': partner_list,
                'response_code': response_code}

    @http.route('/GetCountry', type='json', auth='public', cors='*')
    def get_country(self, **kwargs):
        ''' function will return Country '''
        country_obj = request.env['res.country']
        status, message, country_list = '', '', []
        response_code = 0
        if kwargs:
            _logger.info("Arguments: %s", kwargs)
            if not kwargs.get('token', ''):
                return {'status': 'FAILED', 'message': 'No token supplied!'}
            try:
                user = request.env['res.users'].sudo().search([('token', '=', kwargs.get('token', ''))])
                if not user:
                    status = 'FAILED'
                    message = 'Login Failed! '
                    response_code = 1007
                else:
                    # countries = country_obj.sudo(user.id).search([])
                    countries = country_obj.sudo().search([])
                    if countries:
                        for country_ in countries:
                            country_data = {
                                'country_id': country_.id,
                                'name': country_.name,
                            }
                            country_list.append(country_data)
                        status = 'SUCCESS'
                        message = 'Countries Found!'
                    else:
                        status = 'FAILED'
                        message = 'Countries not Found!'
            except Exception as e:
                _logger.info("Error: %s", e.args)
                status = 'FAILED'
                message = 'Error: ' + str(e.args)
        else:
            status = 'FAILED'
            message = 'No params supplied, Please contact Administrator!'
        return {'status': status, 'message': message, 'country_list': country_list,
                'response_code': response_code}

    @http.route('/GetCity', type='json', auth='public', cors='*')
    def get_city(self, **kwargs):
        ''' function will return City '''
        city_obj = request.env['res.city']
        status, message, city_list = '', '', []
        response_code = 0
        if kwargs:
            _logger.info("Arguments: %s", kwargs)
            if not kwargs.get('token', ''):
                return {'status': 'FAILED', 'message': 'No token supplied!'}
            try:
                user = request.env['res.users'].sudo().search([('token', '=', kwargs.get('token', ''))])
                if not user:
                    status = 'FAILED'
                    message = 'Login Failed! '
                    response_code = 1007
                else:
                    # cities = city_obj.sudo(user.id).search([])
                    cities = city_obj.sudo().search([])
                    if cities:
                        for city_ in cities:
                            city_data = {
                                'city_id': city_.id,
                                'name': city_.name,
                            }
                            city_list.append(city_data)
                        status = 'SUCCESS'
                        message = 'Cities Found!'
                    else:
                        status = 'FAILED'
                        message = 'Cities not Found!'
            except Exception as e:
                _logger.info("Error: %s", e.args)
                status = 'FAILED'
                message = 'Error: ' + str(e.args)
        else:
            status = 'FAILED'
            message = 'No params supplied, Please contact Administrator!'
        return {'status': status, 'message': message, 'city_list': city_list,
                'response_code': response_code}

    @http.route('/GetState', type='json', auth='public', cors='*')
    def get_state(self, **kwargs):
        ''' function will return States '''
        state_obj = request.env['res.country.state']
        status, message, state_list = '', '', []
        response_code = 0
        if kwargs:
            _logger.info("Arguments: %s", kwargs)
            if not kwargs.get('token', ''):
                return {'status': 'FAILED', 'message': 'No token supplied!'}
            try:
                user = request.env['res.users'].sudo().search([('token', '=', kwargs.get('token', ''))])
                if not user:
                    status = 'FAILED'
                    message = 'Login Failed! '
                    response_code = 1007
                else:
                    # states = state_obj.sudo(user.id).search([])
                    states = state_obj.sudo().search([])
                    if states:
                        for state_ in states:
                            state_data = {
                                'state_id': state_.id,
                                'name': state_.name,
                            }
                            state_list.append(state_data)
                        status = 'SUCCESS'
                        message = 'States Found!'
                    else:
                        status = 'FAILED'
                        message = 'States not Found!'
            except Exception as e:
                _logger.info("Error: %s", e.args)
                status = 'FAILED'
                message = 'Error: ' + str(e.args)
        else:
            status = 'FAILED'
            message = 'No params supplied, Please contact Administrator!'
        return {'status': status, 'message': message, 'state_list': state_list,
                'response_code': response_code}

    @http.route('/GetTown', type='json', auth='public', cors='*')
    def get_township(self, **kwargs):
        ''' function will return Town '''
        town_obj = request.env['res.town']
        status, message, town_list = '', '', []
        response_code = 0
        if kwargs:
            _logger.info("Arguments: %s", kwargs)
            if not kwargs.get('token', ''):
                return {'status': 'FAILED', 'message': 'No token supplied!'}
            try:
                user = request.env['res.users'].sudo().search([('token', '=', kwargs.get('token', ''))])
                if not user:
                    status = 'FAILED'
                    message = 'Login Failed! '
                    response_code = 1007
                else:
                    # towns = town_obj.sudo(user.id).search([])
                    towns = town_obj.sudo().search([])
                    if towns:
                        for town_ in towns:
                            town_data = {
                                'town_id': town_.id,
                                'name': town_.name,
                            }
                            town_list.append(town_data)
                        status = 'SUCCESS'
                        message = 'Towns Found!'
                    else:
                        status = 'FAILED'
                        message = 'Town not Found!'
            except Exception as e:
                _logger.info("Error: %s", e.args)
                status = 'FAILED'
                message = 'Error: ' + str(e.args)
        else:
            status = 'FAILED'
            message = 'No params supplied, Please contact Administrator!'
        return {'status': status, 'message': message, 'town_list': town_list,
                'response_code': response_code}

    @http.route('/CreatePartner', type='json', auth='public', cors='*')
    def partner_creation(self, **kwargs):
        '''this function is used to create partner '''
        partner_obj = request.env['res.partner']
        assignment_obj = request.env['fleet.assigned.task']
        status, message, response_code, partner_id, partner_list = '', '', 0, '', []
        if kwargs:
            _logger.info("Arguments: %s", kwargs)
            if not kwargs.get('token', ''):
                return {'status': 'FAILED', 'message': 'No token supplied!'}
            if not kwargs.get('partner_name', ''):
                return {'status': 'FAILED', 'message': 'Please Enter Customer Name!'}
            if not kwargs.get('email', ''):
                return {'status': 'FAILED', 'message': 'Please Enter Email Address!'}
            try:
                token = kwargs.get('token', '')
                assignment_id = kwargs.get('assignment_id', '')
                user = request.env['res.users'].sudo().search([('token', '=', token)])
                assignment = assignment_obj.sudo().search([('id', '=', assignment_id)])
                if not user:
                    status = 'FAILED'
                    message = 'Login Failed! '
                    response_code = 1007
                elif not assignment:
                    status = 'FAILED'
                    message = 'Assignment not found!'
                    response_code = 1007
                elif not assignment.routeId:
                    status = 'FAILED'
                    message = 'Route not found!'
                    response_code = 1007
                if not user:
                    status = 'FAILED'
                    message = 'Login Failed!'
                    response_code = 1007
                else:
                    try:
                        # partner = partner_obj.sudo(user).search([
                        #     ('email', '=', kwargs.get('email', ''))
                        # ], limit=1)
                        partner = partner_obj.sudo().search([
                            ('email', '=', kwargs.get('email', ''))
                        ], limit=1)
                        # state = request.env['res.country.state'].sudo().search([
                        #     ('id', '=', kwargs.get('state', ''))
                        # ], limit=1)
                        # country = request.env['res.country'].sudo().search([
                        #     ('id', '=', kwargs.get('country', ''))
                        # ], limit=1)
                        # # city = request.env['res.city'].sudo().search([
                        # #     ('id', '=', kwargs.get('city', ''))
                        # # ], limit=1)
                        # town = request.env['res.town'].sudo().search([
                        #     ('id', '=', kwargs.get('town', ''))
                        # ], limit=1)
                        if not partner:
                            partners_dict = {
                                'name': kwargs.get('partner_name', ''),
                                'active': True,
                                'user_id': user.id,
                                'street': kwargs.get('address_line_1', ''),
                                'street2': kwargs.get('address_line2', ''),
                                'phone': kwargs.get('phone', ''),
                                'mobile': kwargs.get('mobile', ''),
                                # 'city': city and city.id or False,
                                # 'state_id': state and state.id or False,
                                # 'town': town and town.id or False,
                                'zip': kwargs.get('zip', ''),
                                # 'country_id': country.id or False,
                                'email': kwargs.get('email', ''),
                                'partner_latitude': kwargs.get('latitude', ''),
                                'partner_longitude': kwargs.get('longitude', ''),
                                'website': kwargs.get('website', '')
                            }
                            # partner_id = partner_obj.sudo(user.id).create(partners_dict)
                            partner_id = partner_obj.sudo().create(partners_dict)
                            _logger.info("Partner: %s", partner_id)
                            assignment.routeId.partner_ids = [(4, partner_id.id)]
                            if partner_id:
                                status = 'Success'
                                message = 'Partner created Successfully!'
                                response_code = 200
                        elif partner:
                            return {'status': "Failed", 'message': "Partner already Present", 'response_code': 200}
                    except Exception as e:
                        _logger.info("Error: %s", e.args)
                        status = 'FAILED'
                        message = 'Error: ' + str(e.args)
            except Exception as e:
                _logger.info("Error: %s", e.args)
                status = 'FAILED'
                message = 'Error: ' + str(e.args)
        else:
            status = 'FAILED'
            message = 'No params supplied, Please contact administrator !'
        return {'status': status, 'message': message, 'name': kwargs.get('partner_name', ''), 'response_code': response_code}

    @http.route('/GetPartner', type='json', auth='public', cors='*')
    def get_partner(self, **kwargs):
        partner_obj = request.env['res.partner']
        status, message, partner_list = '', '', []
        response_code = 0
        if kwargs:
            _logger.info("Arguments: %s", kwargs)
            if not kwargs.get('token', ''):
                return {'status': 'FAILED', 'message': 'No token supplied!'}
            try:
                token = kwargs.get('token', '')
                assignment_id = kwargs.get('assignment_id', '')
                user = request.env['res.users'].sudo().search([('token', '=', token)])
                if not user:
                    status = 'FAILED'
                    message = 'Login Failed! '
                    response_code = 1007
                else:
                    partners = partner_obj.sudo().search([])
                    if partners:
                        for partner in partners:
                            partner_dict = {
                                'partner_id': partner.id,
                                'partner_name': partner.name,
                                'address_line1': partner.street or '',
                                'address_line2': partner.street2 or '',
                                'town': partner.town.name or '',
                                'city': partner.city.name or '',
                                'state': partner.state_id.name or '',
                                'zip': partner.zip or '',
                                'country': partner.country_id.name or '',
                                'phone': partner.phone or '',
                                'mobile': partner.mobile or '',
                                'email': partner.email or '',
                                'website': partner.website or '',
                                'latitude': partner.partner_latitude,
                                'longitude': partner.partner_longitude,
                            }
                            partner_list.append(partner_dict)
                        status = 'SUCCESS'
                        message = 'Partner Details'
                    else:
                        return {'status': 'Failed', 'message': 'No Partner found!', 'Count': partner_list,
                                'response_code': response_code}
            except Exception as e:
                _logger.info("Error: %s", e.args)
                status = 'FAILED'
                message = 'Error: ' + str(e.args)
        else:
            status = 'FAILED'
            message = 'No params supplied, Please contact administrator !'
        return {'status': status, 'message': message, 'partner_list': partner_list,
                'response_code': response_code}

    @http.route('/UpdatePartnerinRoute', type='json', auth='public', cors='*')
    def update_partner_in_route(self, **kwargs):
        partner_obj = request.env['res.partner']
        assignment_obj = request.env['fleet.assigned.task']
        status, message, partner_list = '', '', []
        response_code = 0
        if kwargs:
            _logger.info("Arguments: %s", kwargs)
            if not kwargs.get('token', ''):
                return {'status': 'FAILED', 'message': 'No token supplied!'}
            try:
                token = kwargs.get('token', '')
                assignment_id = kwargs.get('assignment_id', '')
                partner_id = kwargs.get('partner_id', '')
                user = request.env['res.users'].sudo().search([('token', '=', token)])
                assignment = assignment_obj.sudo().search([('id', '=', assignment_id)])
                partner = partner_obj.sudo().search([('id', '=', partner_id)])
                if not user:
                    status = 'FAILED'
                    message = 'Login Failed! '
                    response_code = 1007
                elif not assignment:
                    status = 'FAILED'
                    message = 'Assignment not found!'
                    response_code = 1007
                elif not assignment.routeId:
                    status = 'FAILED'
                    message = 'Route not found!'
                    response_code = 1007
                elif not partner:
                    status = 'FAILED'
                    message = 'Partner not selected!'
                    response_code = 1007
                else:
                    assignment.routeId.partner_ids = [(4, partner.id)]
                    status = 'SUCCESS'
                    message = 'Partner added successfully!'
            except Exception as e:
                _logger.info("Error: %s", e.args)
                status = 'FAILED'
                message = 'Error: ' + str(e.args)
        else:
            status = 'FAILED'
            message = 'No params supplied, Please contact administrator !'
        return {'status': status, 'message': message, 'response_code': response_code}

    @http.route('/GetPartnerTask', type='json', auth='public', cors='*')
    def get_partner_task(self, **kwargs):
        partner_obj = request.env['res.partner']
        assignment_obj = request.env['fleet.assigned.task']
        assignment_task_obj = request.env['fleet.assignment.item']
        status, message, task_list, tasks_complete = '', '', [], ''
        response_code = 0
        if kwargs:
            _logger.info("Arguments: %s", kwargs)
            if not kwargs.get('token', ''):
                return {'status': 'FAILED', 'message': 'No token supplied!'}
            try:
                token = kwargs.get('token', '')
                assignment_id = kwargs.get('assignment_id', '')
                partner_id = kwargs.get('partner_id', '')
                user = request.env['res.users'].sudo().search([('token', '=', token)])
                assignment = assignment_obj.sudo().search([('id', '=', assignment_id)])
                partner = partner_obj.sudo().search([('id', '=', partner_id)])
                action_id = request.env.ref('yoma_salesman_assignment.view_promotion_action',  raise_if_not_found=False)

                if not user:
                    status = 'FAILED'
                    message = 'Login Failed! '
                    response_code = 1007
                elif not assignment:
                    status = 'FAILED'
                    message = 'Assignment not found!'
                    response_code = 1007
                elif not assignment.routeId:
                    status = 'FAILED'
                    message = 'Route not found!'
                    response_code = 1007
                elif not partner:
                    status = 'FAILED'
                    message = 'Partner not selected!'
                    response_code = 1007
                else:
                    if assignment:
                        # task_ids = assignment_task_obj.search([
                        #     ('assigned_task_id', '=', assignment.id),
                        #     ('partner_id', '=', partner.id)
                        # ])
                        task_ids = assignment_task_obj.sudo().search([
                            ('assigned_task_id', '=', assignment.id),
                            ('partner_id', '=', partner.id)
                        ])
                        if all(task.status == 'completed' for task in task_ids):
                            tasks_complete = 1
                        else:
                            tasks_complete = 0
                        for task in task_ids:
                            _logger.info("Error: %s", task)
                            #Yoma custom code
                            special_list = []
                            for special in task.task_id.specials:
                                specials={
                                    'name': special.name,
                                    'id': special.id
                                }
                                special_list.append(specials)
                            task_dict = {
                                'record_id': task.id,
                                'name': task.task_id.name,
                                # 'task_description': task.task_id.description,
                                'status': task.status,
                                'specials': special_list,
                                'partner_id': partner_id,
                                'action': action_id.id,
                            }
                            if task.status != 'completed':
                                task_dict['task_status'] = 0
                            else:
                                task_dict['task_status'] = 1

                            task_list.append(task_dict)
                    status = 'SUCCESS'
                    message = 'Task Details'
            except Exception as e:
                _logger.info("Error: %s", e.args)
                status = 'FAILED'
                message = 'Error: ' + str(e.args)
        else:
            status = 'FAILED'
            message = 'No params supplied, Please contact administrator !'
        return {'status': status, 'message': message, 'tasks_complete': tasks_complete,
                'task_list': task_list, 'response_code': response_code}

    # @http.route('/UpdatePartnerTask', type='json', auth='public', cors='*')
    # def update_task_values(self, **kwargs):
    #     partner_obj = request.env['res.partner']
    #     assignment_obj = request.env['fleet.assigned.task']
    #     assignment_task_obj = request.env['fleet.assignment.item']
    #     status, message, tasks_complete = '', '', ''
    #     response_code = 0
    #     if kwargs:
    #         _logger.info("Arguments: %s", kwargs)
    #         if not kwargs.get('token', ''):
    #             return {'status': 'FAILED', 'message': 'No token supplied!'}
    #         try:
    #             token = kwargs.get('token', '')
    #             assignment_id = kwargs.get('assignment_id', '')
    #             partner_id = kwargs.get('partner_id', '')
    #             task_id = kwargs.get('task_id', '')
    #             task_title = kwargs.get('task_title', '')
    #             task_description = kwargs.get('task_description', '')
    #             user = request.env['res.users'].sudo().search([('token', '=', token)])
    #             assignment = assignment_obj.sudo().search([('id', '=', assignment_id)])
    #             partner = partner_obj.sudo().search([('id', '=', partner_id)])
    #             task = assignment_task_obj.sudo().search([('id', '=', task_id)])
    #             if not user:
    #                 status = 'FAILED'
    #                 message = 'Login Failed! '
    #                 response_code = 1007
    #             elif not assignment:
    #                 status = 'FAILED'
    #                 message = 'Assignment not found!'
    #                 response_code = 1008
    #             elif not assignment.routeId:
    #                 status = 'FAILED'
    #                 message = 'Route not found!'
    #                 response_code = 1009
    #             elif not partner:
    #                 status = 'FAILED'
    #                 message = 'Partner not selected!'
    #                 response_code = 1010
    #             elif not task:
    #                 status = 'FAILED'
    #                 message = 'Task not found!'
    #                 response_code = 1011
    #             else:
    #                 # task_ids = assignment_task_obj.search([
    #                 #     ('assigned_task_id', '=', assignment.id),
    #                 #     ('partner_id', '=', partner.id)
    #                 # ])
    #                 task_ids = assignment_task_obj.sudo().search([
    #                     ('assigned_task_id', '=', assignment.id),
    #                     ('partner_id', '=', partner.id)
    #                 ])
    #                 if all(task.status == 'completed' for task in task_ids):
    #                     tasks_complete = 1
    #                 else:
    #                     tasks_complete = 0
    #
    #                 task.date = datetime.now()
    #                 task.note = task_title
    #                 task.sudo().complete_task()
    #                 status = 'SUCCESS'
    #                 message = 'Task updated successfully!'
    #         except Exception as e:
    #             _logger.info("Error: %s", e.args)
    #             status = 'FAILED'
    #             message = 'Error: ' + str(e.args)
    #     else:
    #         status = 'FAILED'
    #         message = 'No params supplied, Please contact administrator!'
    #     return {'status': status, 'message': message,
    #             'tasks_complete': tasks_complete, 'response_code': response_code}
    @http.route('/UpdatePartnerTask', type='json', auth='public', cors='*')
    def update_task_values(self, **kwargs):
        partner_obj = request.env['res.partner']
        assignment_obj = request.env['fleet.assigned.task']
        assignment_task_obj = request.env['fleet.assignment.item']
        status, message, tasks_complete = '', '', ''
        response_code = 0
        print(kwargs)
        if kwargs:
            _logger.info("Arguments: %s", kwargs)
            if not kwargs.get('token', ''):
                return {'status': 'FAILED', 'message': 'No token supplied!'}
            try:
                token = kwargs.get('token', '')
                assignment_id = kwargs.get('assignment_id', '')
                partner_id = kwargs.get('partner_id', '')
                task_id = kwargs.get('task_id', '')
                task_description = kwargs.get('task_description', '')
                user = request.env['res.users'].sudo().search([('token', '=', token)])
                assignment = assignment_obj.sudo().search([('id', '=', assignment_id)])
                partner = partner_obj.sudo().search([('id', '=', partner_id)])
                task = assignment_task_obj.sudo().search([('id', '=', task_id)])
                if not user:
                    status = 'FAILED'
                    message = 'Login Failed! '
                    response_code = 1007
                elif not assignment:
                    status = 'FAILED'
                    message = 'Assignment not found!'
                    response_code = 1008
                elif not assignment.routeId:
                    status = 'FAILED'
                    message = 'Route not found!'
                    response_code = 1009
                elif not partner:
                    status = 'FAILED'
                    message = 'Partner not selected!'
                    response_code = 1010
                elif not task:
                    status = 'FAILED'
                    message = 'Task not found!'
                    response_code = 1011
                else:
                    # task_ids = assignment_task_obj.search([
                    #     ('assigned_task_id', '=', assignment.id),
                    #     ('partner_id', '=', partner.id)
                    # ])
                    task_ids = assignment_task_obj.sudo().search([
                        ('assigned_task_id', '=', assignment.id),
                        ('partner_id', '=', partner.id)
                    ])
                    if all(task.status == 'completed' for task in task_ids):
                        tasks_complete = 1
                    else:
                        tasks_complete = 0
                    task.date = datetime.now()
                    task.note = task_description
                    if kwargs.get('attachments'):
                        for attach in kwargs.get('attachments'):
                            attach_obj = request.env['ir.attachment'].sudo().create({
                                'name': attach.get('name', ''),
                                'type': 'binary',
                                'datas': attach.get('datas'),
                                'res_model': 'fleet.assignment.item',
                                'res_id': task_id
                            })
                            task.attachments = [(4, attach_obj.id)]

                    task.sudo().complete_task()
                    status = 'SUCCESS'
                    message = 'Task updated successfully!'
            except Exception as e:
                _logger.info("Error: %s", e.args)
                status = 'FAILED'
                message = 'Error: ' + str(e.args)
        else:
            status = 'FAILED'
            message = 'No params supplied, Please contact administrator!'
        return {'status': status, 'message': message,
                'tasks_complete': tasks_complete, 'response_code': response_code}

    @http.route('/SavePartnerTask', type='json', auth='public', cors='*')
    def save_task_values(self, **kwargs):
        partner_obj = request.env['res.partner']
        assignment_obj = request.env['fleet.assigned.task']
        assignment_task_obj = request.env['fleet.assignment.item']
        status, message, tasks_complete = '', '', ''
        response_code = 0
        if kwargs:
            _logger.info("Arguments: %s", kwargs)
            if not kwargs.get('token', ''):
                return {'status': 'FAILED', 'message': 'No token supplied!'}
            try:
                token = kwargs.get('token', '')
                assignment_id = kwargs.get('assignment_id', '')
                partner_id = kwargs.get('partner_id', '')
                task_id = kwargs.get('task_id', '')
                task_description = kwargs.get('task_description', '')
                user = request.env['res.users'].sudo().search([('token', '=', token)])
                assignment = assignment_obj.sudo().search([('id', '=', assignment_id)])
                partner = partner_obj.sudo().search([('id', '=', partner_id)])
                task = assignment_task_obj.sudo().search([('id', '=', task_id)])
                if not user:
                    status = 'FAILED'
                    message = 'Login Failed! '
                    response_code = 1007
                elif not assignment:
                    status = 'FAILED'
                    message = 'Assignment not found!'
                    response_code = 1008
                elif not assignment.routeId:
                    status = 'FAILED'
                    message = 'Route not found!'
                    response_code = 1009
                elif not partner:
                    status = 'FAILED'
                    message = 'Partner not selected!'
                    response_code = 1010
                elif not task:
                    status = 'FAILED'
                    message = 'Task not found!'
                    response_code = 1011
                else:
                    # task_ids = assignment_task_obj.search([
                    #     ('assigned_task_id', '=', assignment.id),
                    #     ('partner_id', '=', partner.id)
                    # ])
                    task_ids = assignment_task_obj.sudo().search([
                        ('assigned_task_id', '=', assignment.id),
                        ('partner_id', '=', partner.id)
                    ])
                    if all(task.status == 'completed' for task in task_ids):
                        tasks_complete = 1
                    else:
                        tasks_complete = 0
                    task.date = datetime.now()
                    task.note = task_description
                    task.sudo().progress_task()
                    status = 'SUCCESS'
                    message = 'Task updated successfully!'
            except Exception as e:
                _logger.info("Error: %s", e.args)
                status = 'FAILED'
                message = 'Error: ' + str(e.args)
        else:
            status = 'FAILED'
            message = 'No params supplied, Please contact administrator!'
        return {'status': status, 'message': message,
                'tasks_complete': tasks_complete, 'response_code': response_code}

    @http.route('/AddPartnerTask', type='json', auth='public', cors='*')
    def add_partner_task(self, **kwargs):
        partner_obj = request.env['res.partner']
        assignment_obj = request.env['fleet.assigned.task']
        assignment_task_obj = request.env['fleet.assignment.item']
        task_obj = request.env['fleet.task']
        status, message, tasks_complete, task_list = '', '', '', []
        response_code = 0
        print(kwargs)
        if kwargs:
            _logger.info("Arguments: %s", kwargs)
            if not kwargs.get('token', ''):
                return {'status': 'FAILED', 'message': 'No token supplied!'}
            try:
                token = kwargs.get('token', '')
                assignment_id = kwargs.get('assignment_id', '')
                partner_id = kwargs.get('partner_id', '')
                task_title = kwargs.get('task_title', '')
                # task_id = kwargs.get('task_id', '')
                task_description = kwargs.get('task_description', '')
                user = request.env['res.users'].sudo().search([('token', '=', token)])
                assignment = assignment_obj.sudo().search([('id', '=', assignment_id)])
                partner = partner_obj.sudo().search([('id', '=', partner_id)])
                # task = assignment_task_obj.sudo().search([('id', '=', task_id)])
                if not user:
                    status = 'FAILED'
                    message = 'Login Failed! '
                    response_code = 1007
                elif not assignment:
                    status = 'FAILED'
                    message = 'Assignment not found!'
                    response_code = 1008
                elif not assignment.routeId:
                    status = 'FAILED'
                    message = 'Route not found!'
                    response_code = 1009
                elif not partner:
                    status = 'FAILED'
                    message = 'Partner not selected!'
                    response_code = 1010
                # elif not task:
                #     status = 'FAILED'
                #     message = 'Task not found!'
                #     response_code = 1011
                else:
                    # task_ids = assignment_task_obj.search([
                    #     ('assigned_task_id', '=', assignment.id),
                    #     ('partner_id', '=', partner.id)
                    # ])
                    task_ids = assignment_task_obj.sudo().search([
                        ('assigned_task_id', '=', assignment.id),
                        ('partner_id', '=', partner.id)
                    ])
                    if all(task.status == 'completed' for task in task_ids):
                        tasks_complete = 1
                    else:
                        tasks_complete = 0
                    task_dict = {
                        'name': task_title,
                    }
                    task_id = task_obj.sudo().create(task_dict)
                    _logger.info("Error: %s", task_id)
                    task_line_dict = {
                        'assigned_task_id': assignment.id,
                        'partner_id': partner.id,
                        'task_id': task_id.id,
                        'note': task_description,
                    }
                    _logger.info("Error: %s", task_line_dict)
                    new_task = assignment_task_obj.sudo().create(task_line_dict)
                    new_task.sudo().complete_task()
                    if new_task:
                        status = 'SUCCESS'
                        message = 'Task created successfully!'
                    else:
                        status = 'SUCCESS'
                        message = 'Task creation failed, something went wrong!'
            except Exception as e:
                _logger.info("Error: %s", e.args)
                status = 'FAILED'
                message = 'Error: ' + str(e.args)
        else:
            status = 'FAILED'
            message = 'No params supplied, Please contact administrator!'
        return {'status': status, 'message': message,
                'tasks_complete': tasks_complete, 'response_code': response_code}

    @http.route('/CheckOutPartner', type='json', auth='public', cors='*')
    def checkout_partner(self, **kwargs):
        assignment_obj = request.env['fleet.assigned.task']
        # hr_employee = request.env['hr.employee']
        partner_obj = request.env['res.partner']
        partner_visit_obj = request.env['partner.visit']
        assignment_task_obj = request.env['fleet.assignment.item']
        status, message, partner_list,  = '', '', []
        response_code = 0
        # all_tasks_complete = 0
        if kwargs:
            _logger.info("Arguments: %s", kwargs)
            if not kwargs.get('token', ''):
                return {'status': 'FAILED', 'message': 'No token supplied!'}
            if not kwargs.get('assignment_id', ''):
                return {'status': 'FAILED', 'message': 'Assignment Details has not been supplied!'}
            if not kwargs.get('route_id', ''):
                return {'status': 'FAILED', 'message': 'Route Details has not been supplied!'}
            try:
                token = kwargs.get('token', '')
                assignment_id = kwargs.get('assignment_id', '')
                checkout_lat = kwargs.get('cout_latitude', '')
                checkout_long = kwargs.get('cout_longitude', '')
                partner_id = kwargs.get('partner_id', '')
                user = request.env['res.users'].sudo().search([('token', '=', token)])
                assignment = assignment_obj.sudo().search([('id', '=', assignment_id)])
                partner = partner_obj.sudo().search([('id', '=', partner_id)])
                if not user:
                    status = 'FAILED'
                    message = 'Login Failed! '
                    response_code = 1007
                elif not assignment:
                    status = 'FAILED'
                    message = 'Assignment not found!'
                    response_code = 1007
                elif not assignment.routeId:
                    status = 'FAILED'
                    message = 'Route not found!'
                    response_code = 1007
                elif not partner:
                    status = 'FAILED'
                    message = 'Partner not found!'
                    response_code = 1007

                else:
                    # employee = hr_employee.sudo().search([('address_home_id','=',user.partner_id.id)], limit=1)
                    if assignment:
                        task_ids = assignment_task_obj.sudo().search([
                            ('assigned_task_id', '=', assignment.id),
                            ('partner_id', '=', partner.id)
                        ])
                        # task_ids = assignment_task_obj.search([
                        #     ('assigned_task_id', '=', assignment.id),
                        #     ('partner_id', '=', partner.id)
                        # ])
                        if all(task.status == 'completed' for task in task_ids):
                            all_tasks_complete = 1
                        else:
                            all_tasks_complete = 0
                        # visit_id = partner_visit_obj.search([
                        #     ('assignment_id', '=', assignment.id),
                        #     ('employee_id', '=', employee.id),
                        #     ('partner_id', '=', partner.id),
                        # ], limit=1)
                        visit_ids = partner_visit_obj.sudo().search([
                            ('assignment_id', '=', assignment.id),
                            ('user_id', '=', user.id),
                            ('partner_id', '=', partner.id),
                        ])
                        if visit_ids:
                            for visit_id in visit_ids:

                            # if not visit_id.cout_datetime and not visit_id.cout_lat and not visit_id.cout_long:

                                visit_id.cout_datetime = datetime.now()
                                visit_id.cout_lat = checkout_lat
                                visit_id.cout_long = checkout_long
                            status = 'SUCCESS'
                            message = 'Check-out Successful!'
                        else:
                            status = 'Failed'
                            message = 'Visit check-in not found!'
                    else:
                        status = 'FAILED'
                        message = 'Check-out Failed!'
            except Exception as e:
                _logger.info("Error: %s", e.args)
                status = 'FAILED'
                message = 'Error: ' + str(e.args)
        else:
            status = 'FAILED'
            message = 'No params supplied, Please contact administrator !'
        return {'status': status, 'message': message,
                'response_code': response_code, 'all_tasks_complete': all_tasks_complete}

    @http.route('/GetAllCustomers', type='json', auth='public', cors='*')
    def get_all_customers(self, **kwargs):
        ''' function will return all customers in the system '''
        partner_obj = request.env['res.partner']
        status, message, partner_list = '', '', []
        response_code = 0
        if kwargs:
            _logger.info("Arguments: %s", kwargs)
            if not kwargs.get('token', ''):
                return {'status': 'FAILED', 'message': 'No token supplied!'}
            try:
                user = request.env['res.users'].sudo().search([('token', '=', kwargs.get('token', ''))])
                if not user:
                    status = 'FAILED'
                    message = 'Login Failed! '
                    response_code = 1007
                else:
                    partners = partner_obj.sudo().search([])
                    if partners:
                        for partner in partners:
                            partner_dict = {
                                'partner_id': partner.id,
                                'name': partner.display_name,
                                'town': partner.town.name or '',
                                'city': partner.city.name or '',
                                'state': partner.state_id.name or '',
                                'zip': partner.zip or '',
                                'country': partner.country_id.name or '',
                                'phone': partner.phone or '',
                                'mobile': partner.mobile or '',
                                'partner_latitude': partner.partner_latitude,
                                'partner_longitude': partner.partner_longitude,
                            }
                            partner_list.append(partner_dict)
                        status = 'SUCCESS'
                        message = 'Customers Details'
                    else:
                        status = 'FAILED'
                        message = 'No Customers in the system'
            except Exception as e:
                _logger.info("Error: %s", e.args)
                status = 'FAILED'
                message = 'Error: ' + str(e.args)
        else:
            status = 'FAILED'
            message = 'No params supplied, Please contact Administrator!'

        return {'status': status, 'message': message, 'partner_list': partner_list,'response_code': response_code}

    @http.route('/SetCustomerLocation', type='json', auth='public', cors='*')
    def set_customer_location(self, **kwargs):
        ''' function will update the customer latitude and longitude in the system '''
        partner_obj = request.env['res.partner']
        status, message = '', ''
        response_code = 0
        # all_tasks_complete = 0
        if kwargs:
            _logger.info("Arguments: %s", kwargs)
            if not kwargs.get('partner_id', ''):
                return {'status': 'FAILED', 'message': 'partner_id has not been supplied!'}
            try:
                partner_id = kwargs.get('partner_id', '')
                partner = partner_obj.sudo().search([('id', '=', partner_id)])
                if not partner:
                    status = 'FAILED'
                    message = 'Partner not found!'
                    response_code = 1007
                else:
                    partner_latitude = kwargs.get('partner_latitude', '')
                    partner_longitude = kwargs.get('partner_longitude', '')
                    partner.partner_latitude = partner_latitude
                    partner.partner_longitude = partner_longitude
                    status = 'SUCCESS'
                    message = 'Partner GPS location updated successfully!'
            except Exception as e:
                _logger.info("Error: %s", e.args)
                status = 'FAILED'
                message = 'Error: ' + str(e.args)
        else:
            status = 'FAILED'
            message = 'No params supplied, Please contact administrator!'
        return {'status': status, 'message': message, 'response_code': response_code}

    @http.route('/AddSurveyForm', type='json', auth='public', cors='*')
    def add_survey_form(self, **kwargs):
        competitor_product = request.env['custom.product.competitor']
        response_code = 0
        if kwargs:
            _logger.info("Arguments: %s", kwargs)
            if not kwargs.get('token', ''):
                return {'status': 'FAILED', 'message': 'No token supplied!'}
            try:
                token = kwargs.get('token', '')
                assignment = kwargs.get('assignment_id', '')
                shop_name = kwargs.get('shop_id', '')
                assignment_item = kwargs.get('item_id', '')
                shop_code = kwargs.get('shop_code', '')
                contact_name = kwargs.get('contact_name', '')
                contact_no = kwargs.get('contact_no', '')
                township = kwargs.get('township', '')
                sale_team = kwargs.get('sale_team', '')
                information_collector_name = kwargs.get('information_collector_name', '')
                brand_name = kwargs.get('brand_name', '')
                category = kwargs.get('category', '')
                model = kwargs.get('model', '')
                price = kwargs.get('price', '')
                qty_per_month = kwargs.get('qty_per_month', '')
                promotion = kwargs.get('promotion', '')
                feature = kwargs.get('feature', '')
                note = kwargs.get('note', '')
                date = datetime.now()
                user = request.env['res.users'].sudo().search([('token', '=', token)])
                if not user:
                    status = 'FAILED'
                    message = 'Login Failed! '
                    response_code = 1007
                elif not assignment:
                    status = 'FAILED'
                    message = 'Assignment not found!'
                    response_code = 1008
                elif not assignment.routeId:
                    status = 'FAILED'
                    message = 'Route not found!'
                    response_code = 1009

                else:
                    competitor_dict = {
                        'assignment': assignment,
                        'shop_name': shop_name,
                        'assignment_item': assignment_item,
                        'shop_code': shop_code,
                        'contact_name': contact_name,
                        'contact_no': contact_no,
                        'township': township,
                        'sale_team': sale_team,
                        'information_collector_name': information_collector_name,
                        'brand_name': brand_name,
                        'category': category,
                        'model': model,
                        'price': price,
                        'qty_per_month': qty_per_month,
                        'promotion': promotion,
                        'feature': feature,
                        'note': note,
                        'date': date,
                    }
                    competitor_id = competitor_product.sudo().create(competitor_dict)
                    if competitor_id:
                        status = 'SUCCESS'
                        message = 'Partner GPS location updated successfully!'
                    _logger.info("Error: %s", competitor_id)

            except Exception as e:
                _logger.info("Error: %s", e.args)
                status = 'FAILED'
                message = 'Error: ' + str(e.args)
        else:
            status = 'FAILED'
            message = 'No params supplied, Please contact administrator!'
        return {'status': status, 'message': message, 'response_code': response_code}

    @http.route('/GetAllSurveyForms', type='json', auth='public', cors='*')
    def get_survey_form(self, **kwargs):
        competitor_product = request.env['custom.product.competitor']
        status, message, survey_list = '', '', []
        response_code = 0
        if kwargs:
            _logger.info("Arguments: %s", kwargs)
            if not kwargs.get('token', ''):
                return {'status': 'FAILED', 'message': 'No token supplied!'}
            try:
                token = kwargs.get('token', '')
                assignment_id = kwargs.get('assignment_id', '')
                partner_id = kwargs.get('partner_id', '')
                user = request.env['res.users'].sudo().search([('token', '=', token)])
                if not user:
                    status = 'FAILED'
                    message = 'Login Failed! '
                    response_code = 1007
                else:
                    survey_forms = competitor_product.sudo().search([
                        ('shop_name', '=', partner_id.id), ('assignment', '=', assignment_id.id)])
                    if survey_forms:
                        for form in survey_forms:
                            competitor_dict = {
                                'assignment': assignment_id.id,
                                'shop_name': partner_id.id,
                                'assignment_item': form.assignment_item.id,
                                'shop_code': form.shop_code,
                                'contact_name': form.contact_name,
                                'contact_no': form.contact_no,
                                'township': form.township,
                                'sale_team': form.sale_team,
                                'information_collector_name': form.information_collector_name,
                                'brand_name': form.brand_name,
                                'category': form.category,
                                'model': form.model,
                                'price': form.price,
                                'qty_per_month': form.qty_per_month,
                                'promotion': form.promotion,
                                'feature': form.feature,
                                'note': form.note,
                                'date': form.date,
                            }
                            survey_list.append(competitor_dict)
                        status = 'SUCCESS'
                        message = 'Survey Form Details'
                    else:
                        status = 'FAILED'
                        message = 'No User Assignment Found!'
            except Exception as e:
                _logger.info("Error: %s", e.args)
                status = 'FAILED'
                message = 'Error: ' + str(e.args)
        else:
            status = 'FAILED'
            message = 'No params supplied, Please contact administrator!'
        return {'status': status, 'message': message, 'survey_list': survey_list,
                'response_code': response_code}