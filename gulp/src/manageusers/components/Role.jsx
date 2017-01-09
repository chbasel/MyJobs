import React from 'react';
import {flatten, forOwn, union, values} from 'lodash-compat';
import {Link} from 'react-router';
import {Button, Col, FormControl, Row} from 'react-bootstrap';
import FieldWrapper from 'common/ui/FieldWrapper';
import TagSelect from 'common/ui/tags/TagSelect';

import HelpText from './HelpText';

import {connect} from 'react-redux';
import {runConfirmInPlace} from 'common/actions/confirm-actions';


class Role extends React.Component {
  constructor(props) {
    super(props);
    const role = this.props.roles[this.props.params.roleId];
    const assignedActivities = {};
    Object.keys(props.activities).forEach(key => assignedActivities[key] = []);

    if (role) {
      role.activities.forEach(activity => {
        assignedActivities[activity.appAccess].push({
          display: activity.description,
          value: activity.id,
        });
      });
    }

    this.state = {
      apiResponseHelp: '',
      activitiesHelp: '',
      roleName: '',
      roleNameHelp: [],
      assignedUsers: [],
      assignedActivities: assignedActivities,
      activities: [],
    };
    this.onTextChange = this.onTextChange.bind(this);
    this.handleSaveRoleClick = this.handleSaveRoleClick.bind(this);
    this.handleDeleteRoleClick = this.handleDeleteRoleClick.bind(this);
  }
  componentDidMount() {
    this.initialApiLoad();
  }
  onTextChange(event) {
    this.setState({
      roleName: event.target.value,
    });
  }
  async initialApiLoad() {
    const {api} = this.props;
    const action = this.props.location.query.action;

    if (action === 'Edit') {
      const results = await api.get('/manage-users/api/roles/' + this.props.params.roleId + '/');
      const activities = results.activities;

      this.setState({
        apiResponseHelp: '',
        roleName: results.role_name,
        assignedUsers: results.assigned_users,
        activities: activities,
      });
    } else {
      // action === 'Add'
      const results = await api.get('/manage-users/api/roles/');
      // It doesn't matter which role we get
      const roleObject = results[0];

      const activities = roleObject.activities;

      // Loop through all app_access's
      // Make sure there are no assigned_activities
      forOwn(activities, function resetAssignedActivities(activity) {
        activity.assigned_activities = [];
      });

      this.setState({
        apiResponseHelp: '',
        roleName: '',
        assignedUsers: [],
        activities: activities,
      });
    }
  }
  async handleSaveRoleClick() {
    this.setState({
      apiResponseHelp: '',
      activitiesHelp: '',
      roleNameHelp: [],
    });
    // Grab form fields and validate
    // TODO: Warn user? If they remove a user from all roles, they will have to reinvite him.

    const {api} = this.props;
    const {assignedUsers, roleName} = this.state;
    const roleId = this.props.params.roleId;

    if (roleName === '') {
      // If we don't include activities when we setState, activities will reset to default
      this.setState({
        roleNameHelp: ['Role name empty.'],
      });
      return;
    }

    const assignedActivities = flatten(values(this.state.assignedActivities))
      .map(activity => activity.value);

    // User must select AT LEAST ONE activity
    if (assignedActivities.length < 1) {
      this.setState({
        activitiesHelp:
          'No activities selected. Each role must have at least one activity.',
      });
      return;
    }

    // Determine URL based on action
    const action = this.props.location.query.action;

    let url = '';
    if ( action === 'Edit' ) {
      url = '/manage-users/api/roles/edit/' + roleId + '/';
    } else {
      url = '/manage-users/api/roles/create/';
    }

    // Build data to send
    const dataToSend = {
      role_name: roleName,
      assigned_activities: assignedActivities,
      assigned_users: assignedUsers.map(user => user.name),
    };

    // Submit to server
    try {
      const response = await api.post(url, dataToSend);
      const history = this.props.history;

      // TODO: Render a nice disappearing alert with the disappear_text prop. Use the React CSSTransitionGroup addon.
      // http://stackoverflow.com/questions/33778675/react-make-flash-message-disappear-automatically

      if ( response.success === 'true' ) {
        // Reload API
        this.props.callRolesAPI();
        // Redirect user
        history.pushState(null, '/roles');
      } else if ( response.success === 'false' ) {
        this.setState({
          apiResponseHelp: response.message,
        });
      }
    } catch (e) {
      if (e.response && e.response.status === 403) {
        this.setState({
          apiResponseHelp: 'Unable to save role. Insufficient privileges.',
        });
      }
    }
  }

  async handleDeleteRoleClick() {
    const {api, history, dispatch} = this.props;

    const message = 'Are you sure you want to delete this role?';
    if (! await runConfirmInPlace(dispatch, message)) {
      return;
    }

    const roleId = this.props.params.roleId;

    // Submit to server
    try {
      await api.delete( '/manage-users/api/roles/delete/' + roleId + '/');
      await this.props.callRolesAPI();
      history.pushState(null, '/roles');
    } catch (e) {
      if (e.response && e.response.status === 403) {
        this.setState({
          apiResponseHelp: 'Role not deleted. Insufficient privileges.',
        });
      }
    }
  }

  handleChoose(chosen) {
    const {users} = this.props;
    const chosenUsers = chosen.map(user => user.value);
    const originalUsers = this.state.assignedUsers.map(user => user.id);
    const assignedUsers = union(originalUsers, chosenUsers).map(key => ({
      id: key,
      name: users[key].email,
    }));

    this.setState({assignedUsers});
  }

  handleRemove(removed) {
    const assignedUsers = this.state.assignedUsers.slice();
    for (let i = 0; i <= removed.length; i++) {
      const removedUser = removed[i];
      if (typeof(removedUser) === 'undefined') continue;

      for (let j = 0; j <= assignedUsers.length; j++) {
        const assignedUser = assignedUsers[j];
        if (typeof(assignedUser) === 'undefined') continue;

        if ((removedUser.value.toString() === assignedUser.id.toString()) &&
            (removedUser.display === assignedUser.name)) {
          assignedUsers.splice(j, 1);
        }
      }
    }

    this.setState({assignedUsers});
  }

  handleChooseActivities(app, chosen) {
    const chosenActivities = chosen.map(activity => activity.value);
    const originalActivities =
      this.state.assignedActivities[app].map(activity => activity.value);
    const combinedActivities = union(originalActivities, chosenActivities);
    const assignedActivities = combinedActivities.map(key => {
      const currentActivity = this.props.activities[app].find(activity =>
        activity.id === key);
      if (currentActivity) {
        return {
          display: currentActivity.description,
          value: key,
        };
      }
    });

    this.setState({
      assignedActivities: {
        ...this.state.assignedActivities,
        [app]: assignedActivities,
      },
    });
  }

  handleRemoveActivities(app, removed) {
    const assignedActivities = this.state.assignedActivities[app].slice();
    removed.forEach(activity =>
      assignedActivities.splice(assignedActivities.indexOf(activity), 1));
    this.setState({
      assignedActivities: {
        ...this.state.assignedActivities,
        [app]: assignedActivities,
      },
    });
  }

  render() {
    let action = this.props.location.query.action;
    const {activities} = this.props;

    let deleteRoleButton = '';
    if (action === 'Edit') {
      deleteRoleButton = <Button className="pull-right" onClick={this.handleDeleteRoleClick}>Delete Role</Button>;
    } else {
      action = 'Add';
    }

    const roleNameHelp = this.state.roleNameHelp;

    const apiResponseHelp = this.state.apiResponseHelp;

    const activitiesHelp = this.state.activitiesHelp;

    return (
      <Row>
        <Col xs={12}>
          <div className="wrapper-header">
            <h2>{action} Role</h2>
          </div>

          <div className="product-card-full no-highlight">
            <FieldWrapper
              label="Role Name"
              errors={roleNameHelp}
              required>
              <FormControl
                id="id_role_name"
                maxLength="255"
                name="name"
                type="text"
                value={this.state.roleName}
                size={35}
                onChange={this.onTextChange} />
            </FieldWrapper>

            <section>Activities associated with this role</section>
            <HelpText message={activitiesHelp} />
            {Object.keys(activities).map((key, index) =>
              <FieldWrapper label={key} key={index}>
                <TagSelect
                  available={activities[key].map(activity => ({
                    display: activity.description,
                    value: activity.id,
                  }))}
                  selected={this.state.assignedActivities[key]}
                  onChoose={chosen => this.handleChooseActivities(key, chosen)}
                  onRemove={removed =>
                    this.handleRemoveActivities(key, removed)} />
              </FieldWrapper>
            )}

            <section>Users assigned to this role</section>
            <FieldWrapper label="Users" required>
              <TagSelect
                available={Object.keys(this.props.users).map(key => ({
                  value: key,
                  display: this.props.users[key].email,
                }))}
                selected={this.state.assignedUsers.map(user => ({
                  display: user.name,
                  value: String(user.id),
                }))}
                onChoose={chosen => this.handleChoose(chosen)}
                onRemove={removed => this.handleRemove(removed)}
                ref="users" />
            </FieldWrapper>

            <Row>
              <Col xs={12}>
                <span className="primary pull-right">
                  <HelpText message={apiResponseHelp} />
                </span>
              </Col>

              <Col xs={12}>
                <Button className="primary pull-right" onClick={this.handleSaveRoleClick}>Save Role</Button>
                {deleteRoleButton}
                <Link to="roles" className="pull-right btn btn-default">Cancel</Link>
              </Col>
            </Row>
          </div>
        </Col>
      </Row>
    );
  }
}

Role.propTypes = {
  dispatch: React.PropTypes.func.isRequired,
  location: React.PropTypes.object.isRequired,
  params: React.PropTypes.object.isRequired,
  callRolesAPI: React.PropTypes.func,
  history: React.PropTypes.object.isRequired,
  api: React.PropTypes.object,
  users: React.PropTypes.object,
  roles: React.PropTypes.object,
  activities: React.PropTypes.object,
};

export default connect(state => ({
  users: state.company.users,
  roles: state.company.roles,
  activities: state.activities,
}))(Role);
