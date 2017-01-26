import React from 'react';
import {Component} from 'react';
import {connect} from 'react-redux';
import {doSwitchMainDimension} from '../../actions/sidebar-actions';
import moment from 'moment';
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
          <li className="side-dimension-feedback">
            <a className="side-dimension-title feedback" href="http://www.directemployers.org/beta-feedback" target="_blank">Leave Us Feedback</a>
          </li>
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
