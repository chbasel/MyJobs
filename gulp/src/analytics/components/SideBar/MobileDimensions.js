import React from 'react';
import {Component} from 'react';
import {connect} from 'react-redux';
import {doSwitchMainDimension} from '../../actions/sidebar-actions';
import moment from 'moment';
import MobileDimensionList from './MobileDimensionList';

class MobileDimensions extends Component {
  constructor() {
    super();
  }
  activeDimension(mainDimension) {
    const {toggleMenu, dispatch} = this.props;
    let startDate = moment();
    const endDate = moment().format('MM/DD/YYYY H:mm:ss');
    startDate = startDate.subtract(30, 'days');
    startDate = startDate.format('MM/DD/YYYY');
    toggleMenu();
    dispatch(doSwitchMainDimension(mainDimension, startDate, endDate));
  }
  render() {
    const {analytics, activeMobile, toggleMenu} = this.props;
    const activeDimension = analytics.activePrimaryDimension;
    const primaryMobileDimensions = analytics.primaryDimensions.dimensionList.reports.map((report, i) => {
      return (
        <MobileDimensionList selected={activeDimension} active={this.activeDimension.bind(this, report.value)} key={i} dimension={report} />
      );
    });
    return (
      <div id="mobile_menu" className={activeMobile ? 'active-mobile' : ''}>
        <ul className="sidebar-container">
          <li onClick={toggleMenu} className="side-dimension-header">
            <p className="filter-header">Primary Dimensions{activeMobile ? <i className="fa fa-minus mobile-close" aria-hidden="true"></i> : <i className="fa fa-plus mobile-open" aria-hidden="true"></i>}</p>
            <div className="clearfix"></div>
           </li>
          {primaryMobileDimensions}
          <li className="side-dimension-feedback">
            <a className="side-dimension-title feedback" href="http://www.directemployers.org/beta-feedback" target="_blank">Leave Us Feedback</a>
          </li>
        </ul>
      </div>
    );
  }
}

MobileDimensions.propTypes = {
  dispatch: React.PropTypes.func.isRequired,
  analytics: React.PropTypes.object.isRequired,
  activeMobile: React.PropTypes.bool.isRequired,
  toggleMenu: React.PropTypes.func.isRequired,
};

export default connect(state => ({
  analytics: state.pageLoadData,
}))(MobileDimensions);
