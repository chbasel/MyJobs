/* global $ */
/* global companyName */

import React from 'react';
import _ from 'lodash-compat';
import {render} from 'react-dom';
import {Router, Route, IndexRoute, Link} from 'react-router';

import {formatActivityName} from './formatActivityName';

import Overview from './Overview';
import Roles from './Roles';
import Role from './Role';
import Activities from './Activities';
import Users from './Users';
import User from './User';
import NoMatch from './NoMatch';
import AssociatedRolesList from './AssociatedRolesList';
import AssociatedUsersList from './AssociatedUsersList';
import AssociatedActivitiesList from './AssociatedActivitiesList';
import Status from './Status';

export class App extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      rolesTableRows: [],
      tablesOfActivitiesByApp: [],
      usersTableRows: [],
      callRolesAPI: this.callRolesAPI,
      callUsersAPI: this.callUsersAPI,
      company: companyName,
    };
    this.callActivitiesAPI = this.callActivitiesAPI.bind(this);
    this.callRolesAPI = this.callRolesAPI.bind(this);
    this.callUsersAPI = this.callUsersAPI.bind(this);
  }
  componentDidMount() {
    this.callActivitiesAPI();
    this.callRolesAPI();
    this.callUsersAPI();
  }
  componentWillReceiveProps(nextProps) {
    if ( nextProps.reloadAPIs === 'true' ) {
      this.callActivitiesAPI();
      this.callRolesAPI();
      this.callUsersAPI();
    }
  }
  callActivitiesAPI() {
    // Get activities once, and only once
    $.get('/manage-users/api/activities/', function getActivities(results) {
      // Create an array of tables, each a list of activities of a
      // particular app_access
      const activitiesGroupedByAppAccess = _.groupBy(results, 'app_access_name');
      // Build a table for each app present
      const tablesOfActivitiesByApp = [];
      // First assemble rows needed for each table
      for (const appAccessName in activitiesGroupedByAppAccess) {
        if (activitiesGroupedByAppAccess.hasOwnProperty(appAccessName)) {
          // For each app, build list of rows from results
          const activityRows = [];
          // Loop through all activities...
          for (const activity in activitiesGroupedByAppAccess[appAccessName]) {
            if (activitiesGroupedByAppAccess[appAccessName].hasOwnProperty(activity)) {
              activityRows.push(
                <tr key={activitiesGroupedByAppAccess[appAccessName][activity].activity_id}>
                  <td>{formatActivityName(activitiesGroupedByAppAccess[appAccessName][activity].activity_name)}</td>
                  <td>{activitiesGroupedByAppAccess[appAccessName][activity].activity_description}</td>
                </tr>
              );
            }
          }
          // Assemble this app's table
          tablesOfActivitiesByApp.push(
            <span key={appAccessName}>
              <h3>{appAccessName}</h3>
              <table className="table table-striped table-activities">
                <thead>
                  <tr>
                    <th>Activity</th>
                    <th>Description</th>
                  </tr>
                </thead>
                <tbody>
                  {activityRows}
                </tbody>
              </table>
            </span>
          );
        }
      }
      this.setState({
        tablesOfActivitiesByApp: tablesOfActivitiesByApp,
      });
    }.bind(this));
  }
  callRolesAPI() {
    // Get roles once, but reload if needed
    $.get('/manage-users/api/roles/', function getRoles(results) {
      const rolesTableRows = [];
      for (const key in results) {
        if (results.hasOwnProperty(key)) {
          let editRoleLink;
          if (results[key].role_name !== 'Admin') {
            editRoleLink = <Link to={`/role/${results[key].role_id}`} query={{action: 'Edit'}} className="btn">Edit</Link>;
          }
          rolesTableRows.push(
            <tr key={results[key].role_id}>
              <td data-title="Role">{results[key].role_name}</td>
              <td data-title="Associated Activities">
                <AssociatedActivitiesList activities={results[key].activities}/>
              </td>
              <td data-title="Associated Users">
                <AssociatedUsersList users={results[key].assigned_users}/>
              </td>
              <td data-title="Edit">
                {editRoleLink}
              </td>
            </tr>
          );
        }
      }
      this.setState({
        rolesTableRows: rolesTableRows,
      });
    }.bind(this));
  }
  callUsersAPI() {
    // Get users once, but reload if needed
    $.get('/manage-users/api/users/', function getUsers(results) {
      const usersTableRows = [];
      for (const key in results) {
        if (results.hasOwnProperty(key)) {
          results[key].roles = JSON.parse(results[key].roles);
          usersTableRows.push(
            <tr key={key}>
              <td data-title="User Email">{results[key].email}</td>
              <td data-title="Associated Roles">
                <AssociatedRolesList roles={results[key].roles}/>
              </td>
              <td data-title="Status">
                <Status status={results[key].status} lastInvitation={results[key].lastInvitation}/>
              </td>
              <td data-title="Edit">
                <Link to={`/user/${key}`} action="Edit" query={{action: 'Edit'}} className="btn">Edit</Link>
              </td>
            </tr>
          );
        }
      }
      this.setState({
        usersTableRows: usersTableRows,
      });
    }.bind(this));
  }
  render() {
    const {company} = this.state;
    return (
      <div>
        <div className="row">
          <div className="col-sm-12">
            <h1>{company}</h1>
          </div>
        </div>

        <div className="row">
          <div className="col-sm-12">
            <div className="breadcrumbs">
              <span>
                <Link to="/">Manage Users</Link>
              </span>
            </div>
          </div>
        </div>

        <div className="row">
          <div className="col-sm-4 col-xs-12 pull-right">
            <div className="sidebar">
              <h2 className="top">Navigation</h2>
              <Link to="/" className="btn">Overview</Link>
              <Link to="users" className="btn">Users</Link>
              <Link to="roles" className="btn">Roles</Link>
              <Link to="activities" className="btn">Activities</Link>
            </div>
          </div>

          <div className="col-sm-8 col-xs-12">
            <div className="card-wrapper">
              {this.props.children && React.cloneElement(
                this.props.children, {
                  tablesOfActivitiesByApp: this.state.tablesOfActivitiesByApp,
                  rolesTableRows: this.state.rolesTableRows,
                  usersTableRows: this.state.usersTableRows,
                  callRolesAPI: this.callRolesAPI,
                  callUsersAPI: this.callUsersAPI,
                })
              }
            </div>
          </div>
        </div>
        <div className="clearfix"></div>
      </div>
    );
  }
}

App.propTypes = {
  children: React.PropTypes.object.isRequired,
};

render((
  <Router>
    <Route path="/" component={App}>
      <IndexRoute component={Overview} />
      <Route path="activities" component={Activities} />
      <Route path="roles" component={Roles} />
      <Route path="/role/add" component={Role} />
      <Route path="/role/:roleId" component={Role} />
      <Route path="users" component={Users} />
      <Route path="/user/add" component={User} />
      <Route path="/user/:userId" component={User} />
      <Route path="*" component={NoMatch}/>
    </Route>
  </Router>
), document.getElementById('content'));
