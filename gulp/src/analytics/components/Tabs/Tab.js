import React from 'react';
import {Component} from 'react';
import {connect} from 'react-redux';
import {doSwitchActiveTab} from '../../actions/tab-actions';
import {doRemoveSelectedTab} from '../../actions/tab-actions';
// import {switchActiveTab} from '../../actions/tab-actions';
// import {removeSelectedTab} from '../../actions/tab-actions';
import {Link} from 'react-router';

class Tab extends Component {
  constructor() {
    super();
  }
  activeTab(tabId) {
    const {dispatch} = this.props;
    dispatch(doSwitchActiveTab(tabId));
  }
  removeSelectedTab(tabId, event) {
    event.preventDefault();
    const {dispatch} = this.props;
    dispatch(doRemoveSelectedTab(tabId));
  }
  render() {
    const {tabData} = this.props;
    return (
      <div className="tab-holder">
          <Link onClick={this.activeTab.bind(this, tabData.navId)} className={tabData.active ? 'tab active-tab' : 'tab'} to={'/'}>{tabData.PageLoadData.column_names[0].label}</Link>
          <span onClick={this.removeSelectedTab.bind(this, tabData.navId)} className="close-tab">X</span>
        {this.props.children}
      </div>
      );
  }
}

Tab.propTypes = {
  children: React.PropTypes.element.isRequired,
  tabData: React.PropTypes.object.isRequired,
  dispatch: React.PropTypes.func.isRequired,
};

export default connect()(Tab);
