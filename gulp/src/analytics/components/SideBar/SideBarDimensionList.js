import React from 'react';
import {Component} from 'react';

class SideBarDimension extends Component {
  render() {
    const {dimension, active, selected} = this.props;
    return (
      <li onClick={active} className={selected === dimension.value ? 'side-dimension active-main' : 'side-dimension'}>
         <span className="side-circle-btn"></span><span className="side-dimension-title">{dimension.display}</span>
      </li>
    );
  }
}

SideBarDimension.propTypes = {
  dimension: React.PropTypes.object.isRequired,
  /**
   * Active function for sending the information to the API
   */
  active: React.PropTypes.func.isRequired,
  /**
   * Adding a selected to the current primary dimensions to be highlighted in the sidebar clicked when send a string equal to value to API
   */
  selected: React.PropTypes.string.isRequired,
};

export default SideBarDimension;
