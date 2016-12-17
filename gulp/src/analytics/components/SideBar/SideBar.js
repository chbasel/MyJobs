import React from 'react';
import {Component} from 'react';
import {connect} from 'react-redux';
import {doSwitchMainDimension} from '../../actions/sidebar-actions';
import SideBarDimension from './SideBarDimensionList';

class SideBar extends Component {
  constructor(props) {
    super(props);
  }
  activeDimension(mainDimension) {
    const {dispatch} = this.props;
    dispatch(doSwitchMainDimension(mainDimension));
  }
  render() {
    const {analytics} = this.props;
    const activeDimension = analytics.activePrimaryDimension;
    const primaryDimensions = analytics.primaryDimensions.dimensionList.reports.map((report, i) => {
      return (
        <SideBarDimension selected={activeDimension} active={this.activeDimension.bind(this, report.value)} key={i} dimension={report} />
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
