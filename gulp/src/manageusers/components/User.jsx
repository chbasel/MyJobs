import React from 'react';
import {Button, Col, FormControl, Row} from 'react-bootstrap';
import {Link} from 'react-router';
import {difference, flatten} from 'lodash-compat';
import TagSelect from 'common/ui/tags/TagSelect';
import FieldWrapper from 'common/ui/FieldWrapper';

import {connect} from 'react-redux';
import {runConfirmInPlace} from 'common/actions/confirm-actions';
import {
  addRolesAction,
  removeRolesAction,
  validateEmailAction,
  doUpdateUserRoles,
  doAddUser,
  doRemoveUser,
} from '../actions/company-actions';

class User extends React.Component {
  async handleSave() {
    const {dispatch, history, users, validation} = this.props;
    const userId = this.props.params.userId;
    const user = users[userId] || {};
    // TODO: Error handling

    if (userId) {
      // update user
      const removed = difference(user.roles, validation.roles.value);
      const added = difference(validation.roles.value, user.roles);
      dispatch(doUpdateUserRoles(userId, added, removed));
    } else {
      // create user
      dispatch(doAddUser(validation.email.value, validation.roles.value));
    }

    history.pushState(null, '/users/');
  }

  async handleDelete() {
    const {history, dispatch} = this.props;
    const {userId} = this.props.params;
    const message = 'Are you sure you want to delete this user?';
    if (await runConfirmInPlace(dispatch, message)) {
      dispatch(doRemoveUser(userId));

      history.pushState(null, '/users/');
    }
  }

  handleChoose(chosen) {
    const {dispatch} = this.props;
    const roles = chosen.map(role => role.display);
    dispatch(addRolesAction(roles));
  }

  handleRemove(removed) {
    const {dispatch} = this.props;
    const roles = removed.map(role => role.display);
    dispatch(removeRolesAction(roles));
  }

  render() {
    const {dispatch, users, lastAdmin, roles, validation} = this.props;

    const userId = this.props.params.userId;
    const user = users[userId] || {};
    const errors = flatten(Object.keys(validation).map(key =>
      validation[key].errors));
    const available = difference(Object.keys(roles)
      .map(key => roles[key].name), validation.roles.value)
        .map(role => ({
          value: role,
          display: role,
        }));

    const selected = validation.roles.value.map(role => ({
      value: role,
      display: role,
    }));

    return (
      <Row>
        <Col xs={12}>
          <div className="wrapper-header">
            <h2>{userId ? 'Edit' : 'Add'} User</h2>
          </div>
          <div className="product-card-full no-highlight">
            <FieldWrapper
              label="User Email"
              errors={validation.email.errors}
              required>
              <FormControl
                id="id_userEmail"
                maxLength="255"
                name="id_userEmail"
                type="email"
                readOnly={!!userId}
                autoFocus={!userId}
                value={userId ? user.email : validation.email.value}
                onChange={e => dispatch(validateEmailAction(e.target.value))}
                size="35" />
            </FieldWrapper>
            <FieldWrapper
              label="Roles"
              errors={validation.roles.errors}
              required>
              <TagSelect
                available={available}
                selected={selected}
                onChoose={chosen => this.handleChoose(chosen)}
                onRemove={removed => this.handleRemove(removed)}
                ref="roles" />
            </FieldWrapper>

            <Row>
              <Col xs={12}>
                <Button
                  className="primary pull-right"
                  disabled={!!errors.length}
                  onClick={() => this.handleSave()}>
                  Save User
                </Button>
                { lastAdmin ?
                  null :
                  <Button
                    className="pull-right"
                    onClick={() => this.handleDelete()}>
                    Delete User
                  </Button>
                }
                <Link to="users" className="pull-right btn btn-default">
                  Cancel
                </Link>
              </Col>
            </Row>
          </div>
        </Col>
      </Row>
    );
  }
}

User.propTypes = {
  dispatch: React.PropTypes.func.isRequired,
  location: React.PropTypes.object.isRequired,
  params: React.PropTypes.object.isRequired,
  history: React.PropTypes.object.isRequired,
  api: React.PropTypes.object,
  validation: React.PropTypes.object.isRequired,
  users: React.PropTypes.object.isRequired,
  roles: React.PropTypes.object.isRequired,
  lastAdmin: React.PropTypes.bool.isRequired,
};

export default connect(state => ({
  lastAdmin: state.company.lastAdmin,
  users: state.company.users,
  roles: state.company.roles,
  validation: state.company.validation,
}))(User);
