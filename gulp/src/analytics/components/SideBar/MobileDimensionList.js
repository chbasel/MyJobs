import React from 'react';
import {Component} from 'react';

class MobileDimensionList extends Component {
  selectTab() {
    const {active, close} = this.props;
    active();
    close();
  }
  render() {
    const {dimension, selected} = this.props;
    return (
      <li onClick={this.selectTab.bind(this)} className={selected === dimension.value ? 'side-dimension active-main' : 'side-dimension'}>
         <span className="side-circle-btn"></span><span className="side-dimension-title">{dimension.display}</span>
      </li>
    );
  }
}

MobileDimensionList.propTypes = {
  dimension: React.PropTypes.object.isRequired,
  /**
   * Active function for sending the information to the API
   */
  active: React.PropTypes.func.isRequired,
  /**
   * Adding a selected to the current primary dimensions to be highlighted in the sidebar clicked when send a string equal to value to API
   */
  selected: React.PropTypes.string.isRequired,
  /**
   * Close function to close the dimension list once one is selected
   */
  close: React.PropTypes.func,
};

export default MobileDimensionList;
