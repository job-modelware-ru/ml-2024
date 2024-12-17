import { useState } from "react";
import Button from "react-bootstrap/Button";
import Modal from "react-bootstrap/Modal";
import { observer } from "mobx-react-lite";
import { Form } from "react-bootstrap";

interface Props {
  show: boolean;
  onChangeShowState: (state: boolean) => void;
  onChangePassword: (oldPass: string, newPassword: string) => void;
}

const ChangePasswordDialog: React.FC<Props> = (props: Props) => {
  const [oldPass, setOldPass] = useState("");
  const [newPass, setNewPass] = useState("");

  const onClose = () => {
    setOldPass("");
    setNewPass("");
    props.onChangeShowState(false);
  };

  const handleChangePassword = () => {
    if (oldPass === "" || newPass === "") return;

    props.onChangePassword(oldPass, newPass);

    onClose();
  };

  return (
    <Modal show={props.show} onHide={onClose}>
      <Modal.Header closeButton>
        <Modal.Title>Изменить пароль</Modal.Title>
      </Modal.Header>
      <Modal.Body>
        <Form.Group>
          <Form.Label>Введите старый пароль:</Form.Label>
          <Form.Control
            value={oldPass}
            onChange={(e) => setOldPass(e.target.value)}
            type="text"
            placeholder="Старый пароль"
          />
        </Form.Group>
        <Form.Group>
          <Form.Label>Введите новый пароль:</Form.Label>
          <Form.Control
            value={newPass}
            onChange={(e) => setNewPass(e.target.value)}
            type="text"
            placeholder="Старый пароль"
          />
        </Form.Group>
      </Modal.Body>
      <Modal.Footer>
        <Button variant="secondary" onClick={handleChangePassword}>
          Изменить
        </Button>
        <Button variant="primary" onClick={onClose}>
          Отмена
        </Button>
      </Modal.Footer>
    </Modal>
  );
};

export default observer(ChangePasswordDialog);
