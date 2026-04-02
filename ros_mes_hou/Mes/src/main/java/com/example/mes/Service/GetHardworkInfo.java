package com.example.mes.Service;

import com.example.mes.mapper.HardworkMapper;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.dao.DuplicateKeyException;
import org.springframework.web.bind.annotation.*;
import com.example.mes.pojo.Hardwork;
import com.example.mes.pojo.Result;

import java.time.LocalDateTime;
import java.util.List;

@RestController
@CrossOrigin(origins = "*")
public class GetHardworkInfo {
    @Autowired
    private HardworkMapper hardworkmapper;

    public List<Hardwork> selectall(){
        List<Hardwork> hardworks= hardworkmapper.selectAll();
        return hardworks;
    }

    public void addHardwork(Hardwork hardwork) {
        if (hardwork.getId() == null || hardwork.getId().isEmpty()) {
            throw new RuntimeException("设备ID不能为空");
        }
        hardworkmapper.add(hardwork);
    }

    public List<Hardwork> selectBysome(Hardwork hardwork){
        return hardworkmapper.selectBySome(hardwork);
    }
    public String deleteById(String id){
        Integer rows = hardworkmapper.deleteById(id);
        System.out.println(rows);
        if(rows < 1){
            return "该机械编号不存在！";
        }
        return "success";
    }
}
