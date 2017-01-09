import React from 'react';
import {Link} from 'react-router';

import RolesList from './RolesList';

class Roles extends React.Component {
  render() {
    return (
      <div className="row">
        <div className="col-xs-12 ">
          <div className="wrapper-header">
            <h2>Roles</h2>
          </div>
          <div className="product-card-full no-highlight">

            <RolesList rolesTableRows={this.props.rolesTableRows} />
            <div className="row">
              <Link to="role/add" query={{action: 'Add'}} className="primary pull-right btn btn-default">Add Role</Link>
            </div>
          </div>
        </div>
      </div>
    );
  }
}

Roles.propTypes = {
  rolesTableRows: React.PropTypes.array.isRequired,
};

Roles.defaultProps = {
  rolesTableRows: [],
};

export default Roles;
