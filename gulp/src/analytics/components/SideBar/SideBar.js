import React from 'react';
import {Component} from 'react';
import {connect} from 'react-redux';
import {switchMainDimension} from '../../actions/sidebar-actions';
import SideBarDimension from './SideBarDimensionList';

class SideBar extends Component {
  constructor(props) {
    super(props);
  }
  activeDimension() {
    const {dispatch} = this.props;
    dispatch(switchMainDimension());
  }
  render() {
    const {analytics} = this.props;
    const primaryDimensions = analytics.primaryDimensions.dimensionList.reports.map((report, i) => {
      return (
        <SideBarDimension active={this.activeDimension.bind(this)} key={i} dimension={report} />
      );
    });
    return (
      <div id="menu">
        <ul className="sidebar-container">
          <li className="side-dimension-header">
            <p className="filter-header">Primary Dimensions</p>
            <div className="clearfix"></div>
           </li>
          {primaryDimensions}
        </ul>
      </div>
    );
  }
}

SideBar.propTypes = {
  dispatch: React.PropTypes.func.isRequired,
  analytics: React.PropTypes.object.isRequired,
};

export default connect(state => ({
  analytics: state.pageLoadData,
}))(SideBar);