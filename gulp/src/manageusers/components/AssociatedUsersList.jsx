import React from 'react';

class AssociatedUsersList extends React.Component {
  render() {
    const associatedUsersList = this.props.users.map( (user, index) => {
      return (
        <li key={index}>
          {user.name}
        </li>
      );
    });
    return (
      <ul>
        {associatedUsersList}
      </ul>
    );
  }
}

AssociatedUsersList.propTypes = {
  users: React.PropTypes.array.isRequired,
};

export default AssociatedUsersList;
