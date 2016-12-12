import React from 'react';
import {Component} from 'react';
import {connect} from 'react-redux';
// import {switchMainDimension} from '../../actions/sidebar-actions';
import SideBarDimension from './SideBarDimensionList';

class SideBar extends Component {
  constructor(props) {
    super(props);
  }

  handleSelectDimension(value) {
    const {history} = this.props;
    console.log('handleSelectDimension', value, history);
    history.push({pathname: '', state: {dimension: value}});
    // dispatch(switchMainDimension());
  }

  render() {
    const {analytics} = this.props;
    const reports = analytics.primaryDimensions.dimensionList.reports;
    const primaryDimensions = reports.map((report, i) => {
      return (
        <SideBarDimension
          onSelect={(v) => this.handleSelectDimension(v)}
          key={i}
          dimension={report} />
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
  history: React.PropTypes.object.isRequired,
  dispatch: React.PropTypes.func.isRequired,
  analytics: React.PropTypes.object.isRequired,
};

export default connect(state => ({
  analytics: state.pageLoadData,
}))(SideBar);
