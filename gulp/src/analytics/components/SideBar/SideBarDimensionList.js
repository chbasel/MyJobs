import React from 'react';
import {Component} from 'react';

class SideBarDimension extends Component {
  constructor(props) {
    super(props);
  }
  render() {
    const {dimension, onSelect} = this.props;
    return (
      <li onClick={() => onSelect(dimension.value)} className="side-dimension">
        <span>{dimension.display}</span>
      </li>
    );
  }
}

SideBarDimension.propTypes = {
  dimension: React.PropTypes.object.isRequired,
  onSelect: React.PropTypes.func.isRequired,
};

export default SideBarDimension;
