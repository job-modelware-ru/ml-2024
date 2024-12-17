import { observer } from "mobx-react-lite";
import "bootstrap/dist/css/bootstrap.css";
import { Form, Button } from "react-bootstrap";
import { Context } from "../..";
import { useContext, useEffect, useState } from "react";
import ChangePasswordDialog from "../dialogs/ChangePasswordDialog";

const Profile: React.FC = () => {
  const { store } = useContext(Context);
  const [showChangePassDialog, setShowChangePassDialog] = useState(false);

  useEffect(() => {
    store.getProfile();
  }, []);

  const changePassword = (oldPass: string, newPass: string) => {
    if (localStorage.getItem("token")) {
      store.changePassword(oldPass, newPass);
    }
  };

  return (
    <>
      <Form className="col-lg-5">
        <Form.Group className="my-3 mx-3">
          <Form.Label>Адрес электронной почты</Form.Label>
          <Form.Control
            type="text"
            placeholder={store.profile.email}
            disabled
            readOnly
          />
        </Form.Group>
        <Form.Group className="my-3 mx-3">
          <Form.Label>Логин</Form.Label>
          <Form.Control
            type="text"
            placeholder={store.profile.username}
            disabled
            readOnly
          />
        </Form.Group>
        <Button className="mx-3" onClick={() => setShowChangePassDialog(true)}>
          Изменить пароль
        </Button>
      </Form>

      <ChangePasswordDialog
        show={showChangePassDialog}
        onChangeShowState={setShowChangePassDialog}
        onChangePassword={changePassword}
      ></ChangePasswordDialog>
    </>
  );
};

export default observer(Profile);
