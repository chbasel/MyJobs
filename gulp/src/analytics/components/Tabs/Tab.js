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
  activeTab(id, event) {
    const {dispatch} = this.props;
    dispatch(doSwitchActiveTab(id));
    event.preventDefault();
    this.setState({
      selected: id,
    });
  }
  removeSelectedTab(tabId, event) {
    event.preventDefault();
    const {dispatch} = this.props;
    dispatch(doRemoveSelectedTab(tabId));
  }
  _renderTitles() {
    function labels(child, index) {
      const activeClass = (this.state.selected === child.props.id ? 'active-tab' : '');
      return (
        <li className="tab" key={index}>
          <a href="#"
            className={activeClass}
            onClick={this.activeTab.bind(this, child.props.id)}>
            {child.props.label}
          </a>
          <span onClick={this.removeSelectedTab.bind(this, child.props.id)} className="close-tab">X</span>
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
