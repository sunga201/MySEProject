# MySEProject

업데이트 내역

11/12

-Change 'ShowMenu' class
   Add attribute 'sd', 'smd'  (If not added, 'SaveData' or 'ShowMapData' window closes immediately.)

- Create 'SaveData' class
   - Create mapDataSave method
   - Create showMessage method

- Create ShowMapData class
   

- Change Map_data class to static class
   - Channge map_size, start_spot, object_spot, hazard_spot, hazard_spot_h, color blob_h to static attribute
   - Change set_hidden_data, get_hazard_h, get_cb_h, get_map_size, get_object_spot, get_hazard_spot, remove_hidden_spot to static method

11/13

- Update 'SaveData' class
    - Delete showMessage method

- Create 'Show_result' class
    - Create method
        - __init__()
        - show_map() -> matplotlib + PyQt5

11/15

- Update 'ShowResult' class
    - Create method
         - drawPath() : draw saved path on map.
         - removePath() : remove already drawn path on map.

11/16
- Update 'ShowResult' class
    - Create method
         - showRobotMovement() : show robot movement following the current path every one second on map.

11/17
- Create 'MessageController' class
    - Create method
         - showMessage(object, message, toggle) : Show message on object with messagebox. Close object when toggle value is 1.

- Update 'ShowResult' class
    - Create method
         - generateRandomSpot() : Generate random hazard spot and color blob spot on unused point.
         - changePath() : overwrite current saved path with new path and draw new path on map.
         
-Update 'Save Data' class
    - Change method name
         - mapDataSave -> saveInputData
         

11/20
- Create 'ControlRobot' class in 'robot_and_control.py'
    - Create method
        - getPath() -> return current path infomation.
        - createPath(start) -> create path starting from point 'start' with a* algorithm.
        - g(oldSpot, newSpot), h(spot, obj), f(spot), setParentAndOpenList(x, y, mod), cal(start, end), isHazard(x, y), aStar(start, end)
	-> Used in a* algorithm.

11/24
- Create 'ControlPath' class in 'robot_and_control.py'
     - separate function about path from class 'ControlRobot'.

- Create several method in class 'SIM'
     - SIM 클래스의 객체는 정적 메소드 getInstance()를 통해서 생성된다. 해당 메소드는 SIM 클래스내의 SIM 변수 sim이 none인지 확인하고 none이면 새 객체 생성해서 리턴, 아니면 기존의 객체를 리턴한다. 이를 통해 여러 클래스에서 하나의 객체를 공유할 수 있다(싱글턴 패턴). 생성자를 private로 선언       해야 하지만 파이썬에는 private 개념이 없기 때문에 그냥 놔뒀음

     - moveForward 메소드 추가 : 현재 SIM 객체에 저장되어 있는 위치, 방향 정보를 통해서 SIM을 앞으로 한칸 이동시킨다. 각각 10% 확률로 움직이지 않거나, 앞으로 2칸 움직일 수 있다.

     - turnCW 메소드 추가 : sim의 direction 값을 1 늘린다. 값이 4를 넘어가면 다시 1로 되돌린다. 로봇이 시계방향으로 도는 효과를 가진다.

     - positioningSensor 메소드 추가 : 현재 sim의 direction, position 값을 리턴한다.

     - colorBlobSensor 메소드 추가 : 현재 SIM의 위치 전후좌우에 color blob spot이 있는지 확인하고, 있으면 있는 만큼 그 방향을 리턴한다.

     - hazardSensor 메소드 추가 : 현재 SIM의 바로 앞에 위험 지역이 있는지 확인하고 있으면 True, 없으면 False를 리턴한다.

     - getFoundHazardSpot 메소드 추가 : 현재 로봇이 찾은 hazard spot의 리스트를 리턴한다.

- 'ControlPath' 클래스에 메소드 추가
      - isHazard 메소드 추가 : 좌표 (x, y)가 위험지역인지 확인하고 위험지역이면 True, 아니면 False를 리턴한다.

11/27

- 로봇의 오동작 구현
   - 앞으로 움직이는 명령을 내렸을 때 각각 10퍼센트의 확률로 로봇이 움직이지 않거나 앞으로 두 칸 움직일 수 있다. 이 오동작들은 전방 한칸이나 두칸 앞에 위험 지역이 있거나, 맵의 바깥으로 나가게 될 경우 일어나지 않는다. 

- 맵 외곽 생성
   - 맵 외곽쪽에서 화살표가 제대로 보이지 않는 문제점이 있어, 이를 해결하기 위해 plot의 x 범위를 -1~맵의 가로 사이즈 + 1, y범위를 -1 ~ 맵의 세로 사이즈 + 1로 늘리고 맵의 외곽에 선을 그었다. 경로를 새로 표시하기 위해 기존 경로를 지울 때 외곽도 같이 지워지는 문제점이 있어 경로를 새로 그릴      때마다 외곽을 다시 그려주는 식으로 해결했다.

11/29

- 이미지 파일 경로 변경 -> image 폴더로 옮김.
- 실행 파일 생성
- setStyleSheet을 이용하여 UI를 꾸몄음.
- showMapData 구현 완료.

앞으로 구현할 것들
- 유효하지 않은 map data 입력 골라내기

# 실행 방법

main.py를 실행하면 됩니다. 메뉴에서 save data를 선택하여 맵 데이터를 저장한 뒤 show result나 show map data를 수행할 수 있습니다.
지금은 테스트를 위해 기본 값이 들어 있는 상태이므로 맵 데이터를 저장하지 않고도 show result나 show map data를 수행할 수 있습니다.
