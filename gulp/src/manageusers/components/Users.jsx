import React from 'react';
import {connect} from 'react-redux';
import {Col, Row, Table} from 'react-bootstrap';

import {Link} from 'react-router';

import Status from './Status';

class Users extends React.Component {
  render() {
    const {users} = this.props;

    return (
      <Row>
        <Col xs={12}>
          <div className="wrapper-header">
            <h2>Users</h2>
          </div>
          <div className="product-card-full no-highlight">
            <Table striped id="no-more-tables">
              <thead>
                <tr>
                  <th>User Email</th>
                  <th>Associated Roles</th>
                  <th>Status</th>
                  <th></th>
                </tr>
              </thead>
              <tbody>
                {Object.keys(users).map(key =>
                  <tr key={key}>
                    <td data-title="User Email">{users[key].email}</td>
                    <td data-title="Associated Roles">
                      <ul>
                        {users[key].roles.map((role, index) =>
                          <li key={index}>
                            {role}
                          </li>
                        )}
                      </ul>
                    </td>
                    <td data-title="Status">
                      <Status
                        status={users[key].isVerified}
                        lastInvitation={users[key].lastInvitation} />
                    </td>
                    <td data-title="Edit">
                      <Link
                        to={`/user/${key}`}
                        className="btn">
                        Edit
                      </Link>
                    </td>
                  </tr>
                )}
              </tbody>
            </Table>
            <Row>
              <Link
                className="primary pull-right btn btn-default"
                to="/user/add">
                Add User
              </Link>
            </Row>
          </div>
        </Col>
      </Row>
    );
  }
}

Users.propTypes = {
  users: React.PropTypes.object.isRequired,
};

export default connect(state => ({
  users: state.company.users,
}))(Users);
