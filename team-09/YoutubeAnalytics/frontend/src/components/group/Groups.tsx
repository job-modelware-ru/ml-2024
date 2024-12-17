import { observer } from "mobx-react-lite";
import "bootstrap/dist/css/bootstrap.css";
import { Form, Button } from "react-bootstrap";
import CreateGroupDialog from "../dialogs/CreateGroupDialog";
import { useState, useEffect, useContext } from "react";
import { Context } from "../..";
import Group from "./Group";

const Groups: React.FC = () => {
  const { store } = useContext(Context);
  const [showCreateGroupDialog, setShowCreateGroupDialog] = useState(false);

  const createGroup = (title: string, type: string) => {
    store.createGroup(title, type);
  };

  const chooseChannelGroup = (id: number) => {
    store.choosed_type = "channel";
    store.choosed_group_id = id;
  };

  const chooseVideoGroup = (id: number) => {
    store.choosed_type = "video";
    store.choosed_group_id = id;
  };

  useEffect(() => {
    if (localStorage.getItem("token")) {
      store.getGroups("channel");
      store.getGroups("video");
    }
  }, []);

  return (
    <>
      <Form style={{ width: "100%", height: "100%" }}>
        <Form.Group className="my-3 mx-3">
          <Form.Label>Группы каналов</Form.Label>
          <br />
          <Group
            groups={store.channelGroups}
            elemsPerRow={10}
            onChooseGroup={chooseChannelGroup}
          ></Group>
        </Form.Group>
        <Form.Group id="channel_group" className="my-3 mx-3">
          <Form.Label>Группы видео</Form.Label>
          <br />
          <Group
            groups={store.videoGroups}
            elemsPerRow={10}
            onChooseGroup={chooseVideoGroup}
          ></Group>
        </Form.Group>
        <Button
          className="mx-3 my-3"
          onClick={() => setShowCreateGroupDialog(true)}
        >
          Создать группу
        </Button>
      </Form>

      <CreateGroupDialog
        show={showCreateGroupDialog}
        onChangeShowState={setShowCreateGroupDialog}
        onCreateGroup={createGroup}
      ></CreateGroupDialog>
    </>
  );
};

export default observer(Groups);
