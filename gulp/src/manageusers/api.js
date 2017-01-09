export default class Api {
  constructor(api) {
    this.api = api;
  }

  async getActivities() {
    return await this.api.get('/manage-users/api/activities/');
  }

  async getUsers() {
    return await this.api.get('/manage-users/api/users/');
  }

  // TODO: replace getRoles once that page is converted
  async getAllRoles() {
    return await this.api.get('/manage-users/api/roles/all/');
  }

  async updateUserRoles(userId, add, remove) {
    const promise = this.api.upload('/manage-users/api/users/' + userId + '/', {
      add: add,
      remove: remove,
    });

    return (await promise);
  }

  async addUser(email, roles) {
    const promise = this.api.upload('/manage-users/api/users/add/', {
      email: email,
      roles: roles,
    });

    return (await promise);
  }

  async removeUser(userId) {
    const promise = this.api.delete(
      '/manage-users/api/users/remove/' + userId + '/');

    return (await promise);
  }
}
