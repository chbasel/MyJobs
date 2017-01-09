import React from 'react';

class RolesList extends React.Component {
  render() {
    return (
      <div>
        <table className="table table-striped" id="no-more-tables">
          <thead>
            <tr>
              <th>Role</th>
              <th>Associated Activities</th>
              <th>Associated Users</th>
              <th></th>
            </tr>
          </thead>
          <tbody>
            {this.props.rolesTableRows}
          </tbody>
        </table>
      </div>
    );
  }
}

RolesList.propTypes = {
  rolesTableRows: React.PropTypes.array.isRequired,
};

export default RolesList;
