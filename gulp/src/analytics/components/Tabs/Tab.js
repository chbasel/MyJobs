import React from 'react';
import {Component} from 'react';
import {connect} from 'react-redux';
import {doSwitchActiveTab} from '../../actions/tab-actions';
import {doRemoveSelectedTab} from '../../actions/tab-actions';

class Tab extends Component {
  constructor(props) {
    super(props);

    this.state = {
      selected: 1,
    };
  }
  activeTab(id) {
    const {dispatch} = this.props;
    dispatch(doSwitchActiveTab(id));
    this.setState({
      selected: id,
    });
  }
  removeSelectedTab(tabId) {
    const {dispatch} = this.props;
    dispatch(doRemoveSelectedTab(tabId));
  }
  _renderTitles() {
    function labels(child, index) {
      const activeTab = (child.props.active ? 'tab active-tab' : 'tab');
      return (
        <li
          key={index}
          className={activeTab}
          onClick={this.activeTab.bind(this, child.props.id)}>
          <span onClick={this.removeSelectedTab.bind(this, child.props.id)} className="close-tab">X</span>
          <span>{child.props.label}</span>
        </li>
      );
    }
    return (
      <ul className="tab-labels">
        {this.props.children.map(labels.bind(this))}
      </ul>
    );
  }
  _renderContent() {
    return (
      <div className="tab-content-container">
        {this.props.children}
      </div>
    );
  }
  render() {
    return (
      <div className="tabs-section">
        {this._renderTitles()}
        {this._renderContent()}
      </div>
    );
  }
}


Tab.propTypes = {
  children: React.PropTypes.arrayOf(
    React.PropTypes.element.isRequired,
  ),
  // tabData: React.PropTypes.object.isRequired,
  dispatch: React.PropTypes.func.isRequired,
};

export default connect()(Tab);
