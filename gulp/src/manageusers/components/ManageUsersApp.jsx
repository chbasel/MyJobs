import React from 'react';
import {connect} from 'react-redux';
import {Alert, Button} from 'react-bootstrap';

import {MyJobsApi} from 'common/myjobs-api';
import {getCsrf} from 'common/cookie';
import {forOwn} from 'lodash-compat';
import {Link} from 'react-router';

import {Loading} from 'common/ui/Loading';
import {markPageLoadingAction} from 'common/actions/loading-actions';
import User from './User';
import {
  addRolesAction,
  setLastAdminAction,
  clearValidationAction,
  clearErrorsAction,
  setCurrentUserAction,
  validateEmailAction,
  doRefreshUsers,
  doRefreshRoles,
} from '../actions/company-actions';
import {doRefreshActivities} from '../actions/activities-list-actions';
import AssociatedUsersList from './AssociatedUsersList';
import AssociatedActivitiesList from './AssociatedActivitiesList';
import Confirm from 'common/ui/Confirm';


const api = new MyJobsApi(getCsrf());

export class ManageUsersApp extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      rolesTableRows: [],
      currentUserID: null,
      rolesAPIResults: null,
      callRolesAPI: this.callRolesAPI,
      confirmShow: false,
    };
    this.callRolesAPI = this.callRolesAPI.bind(this);
  }

  componentDidMount() {
    const {history} = this.props;
    this.unsubscribeFromHistory = history.listen((...args) =>
      this.handleNewLocation(...args));

    this.callRolesAPI();
  }

  componentWillReceiveProps(nextProps) {
    if ( nextProps.reloadAPIs === 'true' ) {
      this.callRolesAPI();
    }
  }

  componentWillUnmount() {
    this.unsubscribeFromHistory();
  }

  async handleNewLocation(_, loc) {
    const {dispatch} = this.props;
    const lastComponent = loc.components[loc.components.length - 1];
    const userId = loc.params.userId;

    dispatch(markPageLoadingAction(true));

    // refresh company data, including roles, users, and available activities
    await dispatch(doRefreshUsers());
    await dispatch(doRefreshActivities());
    await dispatch(doRefreshRoles());
    dispatch(clearValidationAction());

    switch (lastComponent) {
    case User:
      const {users} = this.props;
      if (users[userId]) {
        const user = users[userId];
        const admins = Object.keys(users).filter(key =>
          users[key].roles.indexOf('Admin') > -1);
        const lastAdmin = admins.length === 1 && userId === admins[0];
        dispatch(setLastAdminAction(lastAdmin));
        dispatch(addRolesAction(user.roles));
        dispatch(setCurrentUserAction(userId));
      } else {
        dispatch(validateEmailAction(''));
        dispatch(addRolesAction([]));
      }

      break;
    default:
      dispatch(setCurrentUserAction(null));
    }

    dispatch(markPageLoadingAction(false));
    this.callRolesAPI();
  }

  async callRolesAPI() {
    // Get roles once, but reload if needed
    const results = await api.get('/manage-users/api/roles/');
    const rolesTableRows = [];

    forOwn(results, function buildListOfRows(role) {
      let editRoleLink;
      if (role.role_name !== 'Admin') {
        editRoleLink = <Link to={`/role/${role.role_id}`} query={{action: 'Edit'}} className="btn">Edit</Link>;
      }
      rolesTableRows.push(
        <tr key={role.role_id}>
          <td data-title="Role">{role.role_name}</td>
          <td data-title="Associated Activities">
            <AssociatedActivitiesList activities={role.activities}/>
          </td>
          <td data-title="Associated Users">
            <AssociatedUsersList users={role.assigned_users}/>
          </td>
          <td data-title="Edit">
            {editRoleLink}
          </td>
        </tr>
      );
    });
    this.setState({
      rolesTableRows: rolesTableRows,
      rolesAPIResults: results,
    });
  }

  render() {
    const {dispatch, errors, loading} = this.props;

    return (
      <div>
        {errors.length ?
        <Alert bsStyle="danger">
          {errors.map(error => <p>{error}</p>)}
          <Button onClick={() => dispatch(clearErrorsAction())}>OK</Button>
        </Alert>
          : null
        }
        <Confirm/>
        <div className="row">
          <div className="col-sm-12">
            <div className="breadcrumbs">
              <span>
                Manage Users
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
              <Link to="help-and-tutorials" className="btn">Help & Tutorials</Link>
            </div>
          </div>

          <div className="col-sm-8 col-xs-12">
            <div className="card-wrapper">
              {loading ? <Loading /> : this.props.children && React.cloneElement(
                this.props.children, {
                  rolesTableRows: this.state.rolesTableRows,
                  callRolesAPI: this.callRolesAPI,
                  api: api,
                  rolesAPIResults: this.state.rolesAPIResults,
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

ManageUsersApp.propTypes = {
  dispatch: React.PropTypes.func.isRequired,
  params: React.PropTypes.object.isRequired,
  history: React.PropTypes.object.isRequired,
  loading: React.PropTypes.bool.isRequired,
  children: React.PropTypes.object.isRequired,
  users: React.PropTypes.object.isRequired,
  errors: React.PropTypes.array.isRequired,
};

export default connect(state => ({
  loading: state.loading.mainPage,
  users: state.company.users,
  errors: state.company.errors,
}))(ManageUsersApp);
